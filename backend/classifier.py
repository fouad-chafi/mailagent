"""
Email classification service using local LLM.
Classifies emails by importance and category.
"""

import logging
from typing import Optional

from config import settings
from database import db
from llm_service import llm_service, LLMServiceError

logger = logging.getLogger(__name__)


IMPORTANCE_SYSTEM_PROMPT = """You are an email classification assistant. Your task is to determine the importance level of an email.

Respond with ONE of these exact words:
- high: Urgent or time-sensitive matters, requests from managers/directors, deadlines within 48 hours, immediate action required
- medium: Work-related questions, meeting requests, client communications, important but not urgent
- low: Newsletters, promotional content, automated notifications, CC emails with no action required, casual conversations

CRITICAL: Respond with ONLY the word (high, medium, or low). No explanation, no punctuation."""

CATEGORY_SYSTEM_PROMPT = """You are an email categorization assistant. Classify emails into the most appropriate category.

Categories:
- professionnel: Work-related emails, clients, projects, meetings
- personnel: Personal emails from friends, family
- newsletter: Newsletters, mailing lists, subscriptions
- notification: Automated notifications, system alerts, receipts
- urgent: Urgent requests with deadlines, time-sensitive issues
- commercial: Sales emails, promotions, marketing
- administratif: Invoices, contracts, administrative documents

CRITICAL: Respond with ONLY the category name in lowercase. No explanation, no punctuation."""

SUMMARY_SYSTEM_PROMPT = """You are an email summarization assistant. Create a concise summary of the email in 2-3 sentences maximum.

Focus on:
- Main topic or request
- Key information or dates
- Action required (if any)

Keep it factual and brief. Write in the same language as the email."""


class Classifier:
    def __init__(self):
        self.llm = llm_service

    async def classify_importance(self, email_data: dict) -> str:
        prompt = self._build_classification_prompt(email_data)

        try:
            result = await self.llm.call_llm(
                prompt=prompt,
                system_prompt=IMPORTANCE_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=settings.LM_STUDIO_MAX_TOKENS_CLASSIFY,
            )
            result = result.strip().lower().replace(".", "").replace(",", "")

            if result not in settings.IMPORTANCE_LEVELS:
                logger.warning(f"Invalid importance level returned: {result}, defaulting to medium")
                return "medium"

            return result
        except LLMServiceError as e:
            logger.error(f"Error classifying importance for email {email_data.get('id')}: {e}")
            return "medium"

    async def classify_category(self, email_data: dict) -> str:
        prompt = self._build_classification_prompt(email_data)

        try:
            result = await self.llm.call_llm(
                prompt=prompt,
                system_prompt=CATEGORY_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=settings.LM_STUDIO_MAX_TOKENS_CLASSIFY,
            )
            result = result.strip().lower().replace(".", "").replace(",", "")

            if result not in settings.CATEGORIES:
                logger.warning(f"Invalid category returned: {result}, defaulting to professionnel")
                return "professionnel"

            return result
        except LLMServiceError as e:
            logger.error(f"Error classifying category for email {email_data.get('id')}: {e}")
            return "professionnel"

    async def generate_summary(self, email_data: dict) -> Optional[str]:
        if not email_data.get("body_text") and not email_data.get("snippet"):
            return None

        prompt = self._build_summary_prompt(email_data)

        try:
            result = await self.llm.call_llm(
                prompt=prompt,
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                temperature=0.5,
                max_tokens=200,
            )
            return result.strip()
        except LLMServiceError as e:
            logger.error(f"Error generating summary for email {email_data.get('id')}: {e}")
            return None

    async def classify_email(self, email_data: dict) -> dict:
        importance, category, summary = await asyncio.gather(
            self.classify_importance(email_data),
            self.classify_category(email_data),
            self.generate_summary(email_data),
        )
        return {
            "importance": importance,
            "category": category,
            "ai_summary": summary,
        }

    async def batch_classify(self, emails: list[dict]) -> list[dict]:
        results = []
        for email_data in emails:
            classification = await self.classify_email(email_data)
            results.append(classification)
        return results

    def _build_classification_prompt(self, email_data: dict) -> str:
        body = email_data.get("body_text") or email_data.get("snippet", "")
        body = self.llm.truncate_for_context(body, 5000)

        return f"""From: {email_data.get('from_addr', 'Unknown')}
Subject: {email_data.get('subject', '(no subject)')}
To: {email_data.get('to_addr', 'Unknown')}

Body:
{body}"""

    def _build_summary_prompt(self, email_data: dict) -> str:
        body = email_data.get("body_text") or email_data.get("snippet", "")
        body = self.llm.truncate_for_context(body, 8000)

        return f"""From: {email_data.get('from_addr', 'Unknown')}
Subject: {email_data.get('subject', '(no subject)')}

Email content:
{body}"""


import asyncio
classifier = Classifier()
