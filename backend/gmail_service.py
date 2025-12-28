"""
Gmail API service for fetching, parsing, and sending emails.
Handles OAuth authentication and rate limiting.
"""

import asyncio
import base64
import email
import email.policy
import logging
import pickle
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import httpx

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery, errors
from googleapiclient.http import BatchHttpRequest

from config import settings
from database import db, Email as EmailModel

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_PICKLE_PATH = settings.GMAIL_TOKEN_FULL_PATH
CREDENTIALS_PATH = settings.GMAIL_CREDENTIALS_FULL_PATH


class GmailServiceError(Exception):
    pass


class GmailAuthError(GmailServiceError):
    pass


class GmailQuotaError(GmailServiceError):
    pass


class GmailService:
    def __init__(self):
        self.service = None
        self._request_queue: list[asyncio.Queue] = []
        self._rate_limit_delay = 0.1
        self._last_request_time = 0
        self._user_profile = None

    def authenticate(self) -> None:
        creds = None
        if TOKEN_PICKLE_PATH.exists():
            with open(TOKEN_PICKLE_PATH, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_PATH.exists():
                    raise GmailAuthError(
                        f"Gmail credentials file not found at {CREDENTIALS_PATH}. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_PICKLE_PATH, "wb") as token:
                pickle.dump(creds, token)

        self.service = discovery.build("gmail", "v1", credentials=creds)

        # Fetch user profile to get user's name and email
        try:
            profile = self.service.users().getProfile(userId="me").execute()
            self._user_profile = {
                "email_address": profile.get("emailAddress", ""),
                "email": profile.get("emailAddress", "").split("@")[0] if profile.get("emailAddress") else "",
                "name": self._extract_name_from_email(profile.get("emailAddress", ""))
            }
            logger.info(f"Gmail authentication successful for {self._user_profile['email_address']}")
        except Exception as e:
            logger.warning(f"Could not fetch user profile: {e}")
            self._user_profile = {"email_address": "", "email": "", "name": "User"}

    def _extract_name_from_email(self, email_addr: str) -> str:
        """Extract a name from email address (e.g., 'john.doe@gmail.com' -> 'John Doe')"""
        if not email_addr:
            return "User"

        local_part = email_addr.split("@")[0]
        # Remove numbers and special characters, capitalize words
        import re
        cleaned = re.sub(r'[0-9._-]+', ' ', local_part)
        words = cleaned.split()
        if words:
            return ' '.join(word.capitalize() for word in words if word)
        return "User"

    def get_user_profile(self) -> dict:
        """Get the authenticated user's profile information"""
        if not self._user_profile:
            if not self.service:
                self.authenticate()
        return self._user_profile

    def _rate_limit(self):
        now = time.time()
        time_since_last = now - self._last_request_time
        if time_since_last < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - time_since_last)
        self._last_request_time = time.time()

    def _parse_message(self, message_data: dict) -> dict:
        msg_id = message_data["id"]
        thread_id = message_data.get("threadId", "")
        snippet = message_data.get("snippet", "")
        labels = message_data.get("labelIds", [])

        payload = message_data.get("payload", {})
        headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

        def get_body(part):
            if part.get("body", {}).get("data"):
                data = part["body"]["data"]
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            for subpart in part.get("parts", []):
                result = get_body(subpart)
                if result:
                    return result
            return None

        body_text = get_body(payload)

        has_attachments = False
        for part in payload.get("parts", []):
            if part.get("filename"):
                has_attachments = True
                break

        date_str = headers.get("Date", "")
        try:
            date_obj = email.utils.parsedate_to_datetime(date_str)
        except (TypeError, ValueError):
            date_obj = None

        # Improved sender detection for newsletters/digests
        from_addr = headers.get("From", "")
        sender_name = self._extract_sender_name(from_addr, body_text or snippet)

        return {
            "id": msg_id,
            "thread_id": thread_id,
            "from_addr": sender_name,
            "from_addr_raw": from_addr,  # Keep original for reference
            "to_addr": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "body_text": body_text or snippet,
            "body_html": None,
            "date": date_obj,
            "labels": labels,
            "has_attachments": has_attachments,
            "snippet": snippet,
        }

    def _extract_sender_name(self, from_addr: str, body_text: str) -> str:
        """
        Extract the real sender name from newsletter/digest emails.
        For regular emails, returns the From header as-is.
        For newsletters (Medium, GitHub, etc.), extracts the relevant sender.
        """
        import re

        # Common newsletter patterns to detect
        newsletter_patterns = [
            (r'<(.+?)@medium\.com>', 'Medium'),
            (r'<notifications@github\.com>', 'GitHub'),
            (r'<noreply@github\.com>', 'GitHub'),
            (r'<.+@linkedin\.com>', 'LinkedIn'),
            (r'<digest@.+>', 'Newsletter'),
            (r'<newsletter@.+>', 'Newsletter'),
            (r'<updates@.+>', 'Updates'),
            (r'<noreply@.+>', 'Service'),
        ]

        from_lower = from_addr.lower()

        # Check if this is a newsletter
        for pattern, service_name in newsletter_patterns:
            if re.search(pattern, from_lower):
                # For newsletters, try to find a more specific sender in the body
                # Look for patterns like "Stories for [Name]" or "Hi [Name],"
                name_patterns = [
                    r'Stories for ([A-Z][a-zA-Z\s]+)',  # Medium: "Stories for Abdou Tryhard"
                    r'Hi ([A-Z][a-zA-Z]+),',  # Generic: "Hi John,"
                    r'Dear ([A-Z][a-zA-Z]+),',  # Generic: "Dear John,"
                    r'Hello ([A-Z][a-zA-Z]+),',  # Generic: "Hello John,"
                ]

                for name_pattern in name_patterns:
                    match = re.search(name_pattern, body_text[:500])  # Search only first 500 chars
                    if match:
                        extracted_name = match.group(1).strip()
                        if extracted_name and len(extracted_name) < 50:  # Sanity check
                            return f"{service_name} ({extracted_name})"

                # If no specific name found, return just the service name
                return service_name

        # For regular emails, clean up the From header
        # Format: "Name <email@domain.com>" or "email@domain.com"
        match = re.match(r'"?([^"<>]+)"?\s*<([^<>]+)>', from_addr)
        if match:
            return match.group(1).strip()
        elif '<' not in from_addr and '>' not in from_addr:
            return from_addr
        else:
            # Fallback: extract from angle brackets
            match = re.match(r'<([^<>]+)>', from_addr)
            if match:
                email = match.group(1)
                return email.split('@')[0]
            return from_addr

    def sync_recent_emails(self, max_results: int = 50) -> list[dict]:
        if not self.service:
            self.authenticate()

        try:
            self._rate_limit()
            results = (
                self.service.users()
                .messages()
                .list(userId="me", maxResults=max_results, q="is:unread")
                .execute()
            )
            messages = results.get("messages", [])
            logger.info(f"Found {len(messages)} recent unread emails")

            emails_data = []
            for msg in messages:
                try:
                    self._rate_limit()
                    msg_data = (
                        self.service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
                    )
                    parsed = self._parse_message(msg_data)
                    emails_data.append(parsed)
                except errors.HttpError as e:
                    if e.resp.status == 429:
                        logger.warning("Rate limit hit, waiting...")
                        time.sleep(5)
                    else:
                        logger.error(f"Error fetching message {msg['id']}: {e}")
                except Exception as e:
                    logger.error(f"Error parsing message {msg['id']}: {e}")

            return emails_data

        except errors.HttpError as e:
            if e.resp.status == 429:
                raise GmailQuotaError("Gmail API quota exceeded. Please try again later.")
            raise GmailServiceError(f"Gmail API error: {e}") from e
        except Exception as e:
            raise GmailServiceError(f"Failed to sync emails: {e}") from e

    def sync_historical_emails(self, days_back: int = 30, batch_size: int = 100) -> list[dict]:
        if not self.service:
            self.authenticate()

        start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y/%m/%d")
        query = f"after:{start_date}"

        all_emails = []
        page_token = None

        try:
            while True:
                try:
                    self._rate_limit()
                    result = (
                        self.service.users()
                        .messages()
                        .list(userId="me", q=query, maxResults=batch_size, pageToken=page_token)
                        .execute()
                    )

                    messages = result.get("messages", [])
                    if not messages:
                        break

                    logger.info(f"Fetched batch of {len(messages)} emails")

                    for msg in messages:
                        try:
                            self._rate_limit()
                            msg_data = (
                                self.service.users()
                                .messages()
                                .get(userId="me", id=msg["id"], format="full")
                                .execute()
                            )
                            parsed = self._parse_message(msg_data)
                            all_emails.append(parsed)
                        except Exception as e:
                            logger.error(f"Error fetching message {msg['id']}: {e}")

                    page_token = result.get("nextPageToken")
                    if not page_token:
                        break

                except errors.HttpError as e:
                    if e.resp.status == 429:
                        logger.warning("Rate limit hit, waiting 10 seconds...")
                        time.sleep(10)
                    else:
                        raise GmailServiceError(f"Gmail API error: {e}") from e

            logger.info(f"Total historical emails fetched: {len(all_emails)}")
            return all_emails

        except Exception as e:
            raise GmailServiceError(f"Failed to sync historical emails: {e}") from e

    def get_email_by_id(self, message_id: str) -> Optional[dict]:
        if not self.service:
            self.authenticate()

        try:
            self._rate_limit()
            msg_data = (
                self.service.users().messages().get(userId="me", id=message_id, format="full").execute()
            )
            return self._parse_message(msg_data)
        except errors.HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Email {message_id} not found")
                return None
            raise GmailServiceError(f"Failed to fetch email {message_id}: {e}") from e
        except Exception as e:
            raise GmailServiceError(f"Failed to fetch email {message_id}: {e}") from e

    def send_email(self, to: str, subject: str, body: str, in_reply_to: Optional[str] = None) -> str:
        if not self.service:
            self.authenticate()

        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["Subject"] = subject

        if in_reply_to:
            message["In-Reply-To"] = in_reply_to
            message["References"] = in_reply_to

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            self._rate_limit()
            result = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )
            logger.info(f"Email sent successfully, message ID: {result['id']}")
            return result["id"]
        except errors.HttpError as e:
            if e.resp.status == 429:
                raise GmailQuotaError("Gmail API quota exceeded. Please try again later.")
            raise GmailServiceError(f"Failed to send email: {e}") from e
        except Exception as e:
            raise GmailServiceError(f"Failed to send email: {e}") from e

    def mark_as_read(self, message_id: str) -> bool:
        if not self.service:
            self.authenticate()

        try:
            self._rate_limit()
            self.service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to mark email {message_id} as read: {e}")
            return False


gmail_service = GmailService()
