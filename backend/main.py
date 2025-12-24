"""
FastAPI server for mailagent application.
Provides REST API for email management and AI-powered features.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import settings
from database import db, Email as EmailModel
from gmail_service import gmail_service, GmailServiceError, GmailAuthError
from classifier import classifier
from response_generator import response_generator
from llm_service import llm_service, LLMConnectionError, LLMServiceError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

Path("logs").mkdir(exist_ok=True)

app = FastAPI(title="MailAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SyncRequest(BaseModel):
    max_results: int = Field(default=50, ge=1, le=100)
    classify: bool = True


class HistoricalSyncRequest(BaseModel):
    days_back: int = Field(default=30, ge=1, le=365)
    classify: bool = True


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    in_reply_to: Optional[str] = None


class ImproveResponseRequest(BaseModel):
    draft: str
    feedback: str


class StatusResponse(BaseModel):
    status: str
    gmail_connected: bool
    llm_connected: bool
    model: Optional[str] = None
    error: Optional[str] = None


def email_to_dict(email: EmailModel) -> dict:
    import json

    return {
        "id": email.id,
        "thread_id": email.thread_id,
        "from_addr": email.from_addr,
        "to_addr": email.to_addr,
        "subject": email.subject,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "date": email.date.isoformat() if email.date else None,
        "labels": json.loads(email.labels) if email.labels else [],
        "importance": email.importance,
        "category": email.category,
        "ai_summary": email.ai_summary,
        "status": email.status,
        "has_attachments": email.has_attachments,
        "created_at": email.created_at.isoformat() if email.created_at else None,
        "updated_at": email.updated_at.isoformat() if email.updated_at else None,
    }


@app.on_event("startup")
async def startup_event():
    db.init_db()
    logger.info("Database initialized")


@app.get("/", response_model=dict)
async def root():
    return {"message": "MailAgent API", "version": "1.0.0"}


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    gmail_connected = False
    llm_connected = False
    model = None
    error = None

    try:
        gmail_service.authenticate()
        gmail_connected = True
    except GmailAuthError as e:
        error = f"Gmail auth error: {e}"
        logger.warning(f"Gmail auth failed: {e}")
    except Exception as e:
        error = f"Gmail error: {e}"
        logger.warning(f"Gmail check failed: {e}")

    try:
        result = await llm_service.verify_connection()
        llm_connected = result["status"] == "ok"
        model = result.get("model")
    except LLMConnectionError as e:
        if not error:
            error = f"LLM connection error: {e}"
        logger.warning(f"LLM check failed: {e}")
    except Exception as e:
        if not error:
            error = f"LLM error: {e}"
        logger.warning(f"LLM check failed: {e}")

    overall_status = "ok" if (gmail_connected and llm_connected) else "degraded" if (gmail_connected or llm_connected) else "error"

    return StatusResponse(
        status=overall_status,
        gmail_connected=gmail_connected,
        llm_connected=llm_connected,
        model=model,
        error=error,
    )


@app.post("/api/sync")
async def sync_emails(request: SyncRequest, background_tasks: BackgroundTasks):
    try:
        start_time = datetime.utcnow()
        emails_data = gmail_service.sync_recent_emails(max_results=request.max_results)
        duration = (datetime.utcnow() - start_time).total_seconds()

        errors = []
        processed_count = 0

        for email_data in emails_data:
            try:
                existing = db.get_email(email_data["id"])
                if existing:
                    continue

                if request.classify:
                    classification = await classifier.classify_email(email_data)
                    email_data.update(classification)

                db.create_email(email_data)
                processed_count += 1
            except Exception as e:
                errors.append(f"Email {email_data.get('id')}: {str(e)}")
                logger.error(f"Error processing email {email_data.get('id')}: {e}")

        db.log_sync(
            emails_fetched=len(emails_data),
            emails_processed=processed_count,
            errors=errors if errors else None,
            duration=duration,
        )

        return {
            "status": "success",
            "fetched": len(emails_data),
            "processed": processed_count,
            "errors": errors,
        }

    except GmailAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except GmailServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during sync: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/sync/historical")
async def sync_historical(request: HistoricalSyncRequest, background_tasks: BackgroundTasks):
    def sync_task(days_back: int, classify: bool):
        try:
            start_time = datetime.utcnow()
            emails_data = gmail_service.sync_historical_emails(days_back=days_back)
            duration = (datetime.utcnow() - start_time).total_seconds()

            errors = []
            processed_count = 0

            for email_data in emails_data:
                try:
                    existing = db.get_email(email_data["id"])
                    if existing:
                        continue

                    if classify:
                        classification = asyncio.run(classifier.classify_email(email_data))
                        email_data.update(classification)

                    db.create_email(email_data)
                    processed_count += 1
                except Exception as e:
                    errors.append(f"Email {email_data.get('id')}: {str(e)}")

            db.log_sync(
                emails_fetched=len(emails_data),
                emails_processed=processed_count,
                errors=errors if errors else None,
                duration=duration,
            )
            logger.info(f"Historical sync complete: {processed_count} emails processed")

        except Exception as e:
            logger.error(f"Historical sync failed: {e}")

    background_tasks.add_task(sync_task, request.days_back, request.classify)

    return {"status": "started", "message": "Historical sync running in background"}


@app.get("/api/emails")
async def list_emails(
    status: Optional[str] = None,
    importance: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    try:
        emails = db.list_emails(status=status, importance=importance, category=category, limit=limit, offset=offset)
        return {"emails": [email_to_dict(e) for e in emails], "count": len(emails)}
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/{email_id}")
async def get_email(email_id: str):
    email = db.get_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email_to_dict(email)


@app.get("/api/emails/{email_id}/responses")
async def get_email_responses(email_id: str):
    try:
        responses = await response_generator.get_or_generate_responses(email_id)
        return {"email_id": email_id, "responses": responses}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting responses for email {email_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/emails/{email_id}/send")
async def send_email_response(email_id: str, request: SendEmailRequest):
    try:
        email = db.get_email(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        sent_id = gmail_service.send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            in_reply_to=request.in_reply_to,
        )

        gmail_service.mark_as_read(email_id)
        db.update_email(email_id, {"status": "read"})

        return {"status": "sent", "message_id": sent_id}
    except GmailServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/emails/{email_id}/improve")
async def improve_email_response(email_id: str, request: ImproveResponseRequest):
    try:
        email = db.get_email(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        improved = await response_generator.improve_response(
            email_data={
                "from_addr": email.from_addr,
                "subject": email.subject,
                "body_text": email.body_text,
            },
            draft=request.draft,
            feedback=request.feedback,
        )
        return {"improved": improved}
    except Exception as e:
        logger.error(f"Error improving response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    with db.get_session() as session:
        total_emails = session.query(EmailModel).count()
        unread_emails = session.query(EmailModel).filter(EmailModel.status == "unread").count()
        high_importance = session.query(EmailModel).filter(EmailModel.importance == "high").count()

        from sqlalchemy import func
        category_counts = session.query(EmailModel.category, func.count(EmailModel.id)).group_by(EmailModel.category).all()
        categories = {cat: count for cat, count in category_counts}

        return {
            "total_emails": total_emails,
            "unread_emails": unread_emails,
            "high_importance": high_importance,
            "categories": categories,
        }


@app.post("/api/preferences/{key}")
async def set_preference(key: str, value: str):
    db.set_preference(key, value)
    return {"status": "saved", "key": key, "value": value}


@app.get("/api/preferences/{key}")
async def get_preference(key: str, default: Optional[str] = None):
    value = db.get_preference(key, default)
    return {"key": key, "value": value}
