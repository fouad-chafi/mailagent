"""
Database module with SQLAlchemy models and initialization.
SQLite database for storing emails, responses, and user preferences.
"""

from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, DateTime, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from contextlib import contextmanager
from typing import Generator
import json
import logging

from config import settings
from pathlib import Path

logger = logging.getLogger(__name__)

Base = declarative_base()

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=True)
    from_addr = Column(String, nullable=False)
    from_addr_raw = Column(String, nullable=True)  # Original From header
    to_addr = Column(String, nullable=True)
    subject = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    date = Column(DateTime, nullable=True)
    labels = Column(Text, nullable=True)
    importance = Column(String, nullable=True)
    category = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)
    status = Column(String, default="unread")
    has_attachments = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_date", "date"),
        Index("idx_status", "status"),
        Index("idx_importance", "importance"),
    )


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, nullable=False)
    variant_number = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    tone = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)


class SyncHistory(Base):
    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_date = Column(DateTime, default=datetime.utcnow)
    emails_fetched = Column(Integer, default=0)
    emails_processed = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)


class EmailDB:
    def __init__(self):
        db_path = DATA_DIR / "emails.db"
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_email(self, email_id: str, session: Session = None) -> dict | None:
        logger.info(f"[DB DEBUG] get_email called for email_id: {email_id}, session provided: {session is not None}")

        # Use a single session scope and convert everything before exiting
        with self.get_session() as session:
            email = session.query(Email).filter(Email.id == email_id).first()

            if not email:
                logger.info(f"[DB DEBUG] Email not found: {email_id}")
                return None

            logger.info(f"[DB DEBUG] Email object found, extracting attributes one by one...")

            try:
                email_id_val = email.id
                logger.debug(f"[DB DEBUG] id OK: {email_id_val}")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting id: {e}")
                raise

            try:
                thread_id_val = email.thread_id
                logger.debug(f"[DB DEBUG] thread_id OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting thread_id: {e}")
                raise

            try:
                from_addr_val = email.from_addr
                logger.debug(f"[DB DEBUG] from_addr OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting from_addr: {e}")
                raise

            try:
                from_addr_raw_val = email.from_addr_raw
                logger.debug(f"[DB DEBUG] from_addr_raw OK")
            except Exception as e:
                from_addr_raw_val = None
                logger.debug(f"[DB DEBUG] from_addr_raw is None (OK for old records)")

            try:
                to_addr_val = email.to_addr
                logger.debug(f"[DB DEBUG] to_addr OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting to_addr: {e}")
                raise

            try:
                subject_val = email.subject
                logger.debug(f"[DB DEBUG] subject OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting subject: {e}")
                raise

            try:
                body_text_val = email.body_text
                logger.debug(f"[DB DEBUG] body_text OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting body_text: {e}")
                raise

            try:
                body_html_val = email.body_html
                logger.debug(f"[DB DEBUG] body_html OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting body_html: {e}")
                raise

            try:
                date_val = email.date
                logger.debug(f"[DB DEBUG] date OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting date: {e}")
                raise

            try:
                labels_val = email.labels
                logger.debug(f"[DB DEBUG] labels OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting labels: {e}")
                raise

            try:
                importance_val = email.importance
                logger.debug(f"[DB DEBUG] importance OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting importance: {e}")
                raise

            try:
                category_val = email.category
                logger.debug(f"[DB DEBUG] category OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting category: {e}")
                raise

            try:
                ai_summary_val = email.ai_summary
                logger.debug(f"[DB DEBUG] ai_summary OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting ai_summary: {e}")
                raise

            try:
                status_val = email.status
                logger.debug(f"[DB DEBUG] status OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting status: {e}")
                raise

            try:
                has_attachments_val = email.has_attachments
                logger.debug(f"[DB DEBUG] has_attachments OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting has_attachments: {e}")
                raise

            try:
                created_at_val = email.created_at
                logger.debug(f"[DB DEBUG] created_at OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting created_at: {e}")
                raise

            try:
                updated_at_val = email.updated_at
                logger.debug(f"[DB DEBUG] updated_at OK")
            except Exception as e:
                logger.error(f"[DB DEBUG] ERROR getting updated_at: {e}")
                raise

            logger.info(f"[DB DEBUG] All attributes extracted successfully, building dict...")

            # Convert to dict using local variables (safe after session closes)
            import json
            result = {
                "id": email_id_val,
                "thread_id": thread_id_val,
                "from_addr": from_addr_val,
                "from_addr_raw": from_addr_raw_val,
                "to_addr": to_addr_val,
                "subject": subject_val,
                "body_text": body_text_val,
                "body_html": body_html_val,
                "date": date_val.isoformat() if date_val else None,
                "labels": json.loads(labels_val) if labels_val else [],
                "importance": importance_val,
                "category": category_val,
                "ai_summary": ai_summary_val,
                "status": status_val,
                "has_attachments": has_attachments_val,
                "created_at": created_at_val.isoformat() if created_at_val else None,
                "updated_at": updated_at_val.isoformat() if updated_at_val else None,
            }
            logger.info(f"[DB DEBUG] Conversion complete, returning dict with {len(result)} keys")
            return result

    def list_emails(
        self,
        status: str | None = None,
        importance: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        with self.get_session() as session:
            query = session.query(Email)
            if status:
                query = query.filter(Email.status == status)
            if importance:
                query = query.filter(Email.importance == importance)
            if category:
                query = query.filter(Email.category == category)
            emails = query.order_by(Email.date.desc()).limit(limit).offset(offset).all()

            # Convert to dict before session closes
            import json
            result = []
            for email in emails:
                result.append({
                    "id": email.id,
                    "thread_id": email.thread_id,
                    "from_addr": email.from_addr,
                    "from_addr_raw": email.from_addr_raw,
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
                })
            return result

    def create_email(self, email_data: dict, session: Session = None) -> Email:
        labels_json = json.dumps(email_data.get("labels", [])) if email_data.get("labels") else None
        email = Email(
            id=email_data["id"],
            thread_id=email_data.get("thread_id"),
            from_addr=email_data["from_addr"],
            from_addr_raw=email_data.get("from_addr_raw"),
            to_addr=email_data.get("to_addr"),
            subject=email_data.get("subject"),
            body_text=email_data.get("body_text"),
            body_html=email_data.get("body_html"),
            date=email_data.get("date"),
            labels=labels_json,
            importance=email_data.get("importance"),
            category=email_data.get("category"),
            ai_summary=email_data.get("ai_summary"),
            status=email_data.get("status", "unread"),
            has_attachments=email_data.get("has_attachments", False),
        )
        if session:
            session.add(email)
            return email
        with self.get_session() as session:
            session.add(email)
            session.commit()
            session.refresh(email)
            return email

    def update_email(self, email_id: str, updates: dict) -> Email | None:
        with self.get_session() as session:
            email = session.query(Email).filter(Email.id == email_id).first()
            if not email:
                return None
            for key, value in updates.items():
                setattr(email, key, value)
            email.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(email)
            return email

    def delete_email(self, email_id: str) -> bool:
        with self.get_session() as session:
            email = session.query(Email).filter(Email.id == email_id).first()
            if not email:
                return False
            session.delete(email)
            session.commit()
            return True

    def save_response(self, email_id: str, variant_number: int, content: str, tone: str) -> dict:
        with self.get_session() as session:
            response = Response(
                email_id=email_id,
                variant_number=variant_number,
                content=content,
                tone=tone,
            )
            session.add(response)
            session.commit()
            session.refresh(response)

            # Extract all attributes while session is open
            resp_id = response.id
            resp_email_id = response.email_id
            resp_variant = response.variant_number
            resp_content = response.content
            resp_tone = response.tone
            resp_generated = response.generated_at
            resp_sent = response.sent
            resp_sent_at = response.sent_at

            # Convert to dict using local variables (safe after session closes)
            return {
                "id": resp_id,
                "email_id": resp_email_id,
                "variant_number": resp_variant,
                "content": resp_content,
                "tone": resp_tone,
                "generated_at": resp_generated.isoformat() if resp_generated else None,
                "sent": resp_sent,
                "sent_at": resp_sent_at.isoformat() if resp_sent_at else None,
            }

    def get_responses(self, email_id: str) -> list[dict]:
        with self.get_session() as session:
            responses = session.query(Response).filter(Response.email_id == email_id).all()

            # Extract all attributes while session is open
            result = []
            for r in responses:
                r_id = r.id
                r_email_id = r.email_id
                r_variant = r.variant_number
                r_content = r.content
                r_tone = r.tone
                r_generated = r.generated_at
                r_sent = r.sent
                r_sent_at = r.sent_at

                result.append({
                    "id": r_id,
                    "email_id": r_email_id,
                    "variant_number": r_variant,
                    "content": r_content,
                    "tone": r_tone,
                    "generated_at": r_generated.isoformat() if r_generated else None,
                    "sent": r_sent,
                    "sent_at": r_sent_at.isoformat() if r_sent_at else None,
                })
            return result

    def delete_unsent_responses(self, email_id: str) -> int:
        with self.get_session() as session:
            count = session.query(Response).filter(
                Response.email_id == email_id,
                Response.sent == False
            ).delete()
            session.commit()
            return count

    def mark_response_sent(self, response_id: int) -> bool:
        with self.get_session() as session:
            response = session.query(Response).filter(Response.id == response_id).first()
            if not response:
                return False
            response.sent = True
            response.sent_at = datetime.utcnow()
            session.commit()
            return True

    def set_preference(self, key: str, value: str) -> None:
        with self.get_session() as session:
            pref = session.query(UserPreference).filter(UserPreference.key == key).first()
            if pref:
                pref.value = value
            else:
                pref = UserPreference(key=key, value=value)
                session.add(pref)
            session.commit()

    def get_preference(self, key: str, default: str | None = None) -> str | None:
        with self.get_session() as session:
            pref = session.query(UserPreference).filter(UserPreference.key == key).first()
            return pref.value if pref else default

    def log_sync(self, emails_fetched: int, emails_processed: int, errors: list[str] | None = None, duration: float | None = None) -> SyncHistory:
        with self.get_session() as session:
            sync = SyncHistory(
                emails_fetched=emails_fetched,
                emails_processed=emails_processed,
                errors=json.dumps(errors) if errors else None,
                duration_seconds=duration,
            )
            session.add(sync)
            session.commit()
            session.refresh(sync)
            return sync


db = EmailDB()
