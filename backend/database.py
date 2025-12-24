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

from config import settings

Base = declarative_base()


class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=True)
    from_addr = Column(String, nullable=False)
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
        self.engine = create_engine(
            settings.DATABASE_URL.replace("sqlite:///", "sqlite:///"),
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

    def get_email(self, email_id: str, session: Session = None) -> Email | None:
        if session:
            return session.query(Email).filter(Email.id == email_id).first()
        with self.get_session() as session:
            return session.query(Email).filter(Email.id == email_id).first()

    def list_emails(
        self,
        status: str | None = None,
        importance: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Email]:
        with self.get_session() as session:
            query = session.query(Email)
            if status:
                query = query.filter(Email.status == status)
            if importance:
                query = query.filter(Email.importance == importance)
            if category:
                query = query.filter(Email.category == category)
            return query.order_by(Email.date.desc()).limit(limit).offset(offset).all()

    def create_email(self, email_data: dict, session: Session = None) -> Email:
        labels_json = json.dumps(email_data.get("labels", [])) if email_data.get("labels") else None
        email = Email(
            id=email_data["id"],
            thread_id=email_data.get("thread_id"),
            from_addr=email_data["from_addr"],
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

    def save_response(self, email_id: str, variant_number: int, content: str, tone: str) -> Response:
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
            return response

    def get_responses(self, email_id: str) -> list[Response]:
        with self.get_session() as session:
            return session.query(Response).filter(Response.email_id == email_id).all()

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
