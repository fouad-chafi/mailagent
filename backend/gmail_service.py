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
        logger.info("Gmail authentication successful")

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

        return {
            "id": msg_id,
            "thread_id": thread_id,
            "from_addr": headers.get("From", ""),
            "to_addr": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "body_text": body_text or snippet,
            "body_html": None,
            "date": date_obj,
            "labels": labels,
            "has_attachments": has_attachments,
            "snippet": snippet,
        }

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
