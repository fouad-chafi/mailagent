"""
Response generation service using local LLM.
Generates email response variants with different tones.
"""

import asyncio
import json
import logging
from typing import Optional

from config import settings
from database import db
from llm_service import llm_service, LLMServiceError

logger = logging.getLogger(__name__)


RESPONSE_SYSTEM_PROMPT = """You are an email response writing assistant. Your task is to generate response variants for the given email.

Generate 3 response variants with different tones:
1. variant1 (formal): Professional and formal tone, suitable for business contexts
2. variant2 (casual): Casual and friendly tone, suitable for colleagues you know well
3. variant3 (neutral): Balanced tone, professional but approachable

Each response should:
- Be concise (maximum 150 words)
- Address all key points in the original email
- Include appropriate closing
- Be ready to send as-is

Respond with valid JSON only, in this exact format:
{{
  "variant1": "Your response text here...",
  "variant2": "Your response text here...",
  "variant3": "Your response text here..."
}}

IMPORTANT: Respond with valid JSON only. No markdown, no code blocks, no explanation."""

IMPROVE_SYSTEM_PROMPT = """You are an email response improvement assistant. Improve the draft response based on user feedback.

Keep the same tone and style but address the feedback provided.
Be concise and ready to send.

Respond with the improved response text only. No explanation."""


class ResponseGenerator:
    def __init__(self):
        self.llm = llm_service

    async def generate_responses(
        self, email_data: dict, num_variants: int = 3
    ) -> dict[str, str]:
        prompt = self._build_generation_prompt(email_data)

        try:
            result = await self.llm.call_llm(
                prompt=prompt,
                system_prompt=RESPONSE_SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=settings.LM_STUDIO_MAX_TOKENS_RESPONSE,
            )
            return self._parse_response_json(result)
        except LLMServiceError as e:
            logger.error(f"Error generating responses for email {email_data.get('id')}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response JSON: {e}")
            raise

    async def improve_response(self, email_data: dict, draft: str, feedback: str) -> str:
        body = email_data.get('body_text', '')[:1000]
        prompt = f"""Original email:
From: {email_data.get('from_addr', 'Unknown')}
Subject: {email_data.get('subject', '(no subject)')}

{body}

Current draft response:
{draft}

User feedback:
{feedback}

Please improve the draft based on the feedback."""

        try:
            result = await self.llm.call_llm(
                prompt=prompt,
                system_prompt=IMPROVE_SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=1000,
            )
            return result.strip()
        except LLMServiceError as e:
            logger.error(f"Error improving response: {e}")
            return draft

    async def get_or_generate_responses(self, email_id: str) -> list[dict]:
        existing = db.get_responses(email_id)
        if existing:
            return [
                {
                    "id": r.id,
                    "variant_number": r.variant_number,
                    "content": r.content,
                    "tone": r.tone,
                    "sent": r.sent,
                }
                for r in existing
            ]

        email_data = db.get_email(email_id)
        if not email_data:
            raise ValueError(f"Email {email_id} not found in database")

        responses_dict = await self.generate_responses(
            {
                "from_addr": email_data.from_addr,
                "subject": email_data.subject,
                "body_text": email_data.body_text,
            }
        )

        tones = ["formal", "casual", "neutral"]
        saved_responses = []

        for i, (variant_key, content) in enumerate(responses_dict.items(), 1):
            tone = tones[i - 1] if i <= len(tones) else "neutral"
            response = db.save_response(email_id, i, content, tone)
            saved_responses.append(
                {
                    "id": response.id,
                    "variant_number": i,
                    "content": content,
                    "tone": tone,
                    "sent": response.sent,
                }
            )

        return saved_responses

    def _build_generation_prompt(self, email_data: dict) -> str:
        body = email_data.get("body_text") or email_data.get("snippet", "")
        # Limit to 2000 chars to stay within 4096 token context
        if len(body) > 2000:
            body = body[:2000] + "..."

        return f"""From: {email_data.get('from_addr', 'Unknown')}
Subject: {email_data.get('subject', '(no subject)')}
To: {email_data.get('to_addr', 'Unknown')}

Email body:
{body}"""

    def _parse_response_json(self, response_text: str) -> dict[str, str]:
        response_clean = response_text.strip()

        if response_clean.startswith("```json"):
            response_clean = response_clean[7:]
        if response_clean.startswith("```"):
            response_clean = response_clean[3:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        response_clean = response_clean.strip()

        try:
            parsed = json.loads(response_clean)
        except json.JSONDecodeError:
            try:
                start = response_clean.find("{")
                end = response_clean.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(response_clean[start:end])
                else:
                    raise
            except json.JSONDecodeError:
                logger.error(f"Could not parse JSON from: {response_clean[:500]}")
                raise

        result = {}
        for key in ["variant1", "variant2", "variant3"]:
            if key in parsed:
                result[key] = parsed[key]
            else:
                result[key] = "Thank you for your email. I will review and get back to you shortly."

        return result


response_generator = ResponseGenerator()
