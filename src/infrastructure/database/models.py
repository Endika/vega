from datetime import UTC, datetime
import uuid

from sqlalchemy import JSON, Column, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), default=datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False,
    )
    status = Column(String(50), default="active", nullable=False)
    # Relationship
    messages = relationship(
        "MessageModel", back_populates="conversation", cascade="all, delete-orphan"
    )
    extracted_data = relationship(
        "ExtractedDataModel", back_populates="conversation", uselist=False
    )
    support_tickets = relationship(
        "CustomerSupportTicketModel", back_populates="conversation", uselist=False
    )

    data = Column(JSON, nullable=True)


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    content = Column(Text, nullable=False)
    sender = Column(String(50), nullable=False)  # "user" or "assistant"
    timestamp = Column(
        TIMESTAMP(timezone=True), default=datetime.now(UTC), nullable=False
    )
    # Relationship
    conversation = relationship("ConversationModel", back_populates="messages")

    data = Column(JSON, nullable=True)


class ExtractedDataModel(Base):
    __tablename__ = "extracted_data"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), primary_key=True
    )
    order_number = Column(String(50), nullable=True)
    problem_category = Column(String(50), nullable=True)
    problem_description = Column(Text, nullable=True)
    urgency_level = Column(String(20), nullable=True)
    extracted_at = Column(
        TIMESTAMP(timezone=True), default=datetime.now(UTC), nullable=False
    )
    confidence_score = Column(Float, default=0.0, nullable=False)
    # Relationship
    conversation = relationship("ConversationModel", back_populates="extracted_data")

    data = Column(JSON, nullable=True)


class CustomerSupportTicketModel(Base):
    __tablename__ = "customer_support_tickets"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), primary_key=True
    )
    order_number = Column(String(50), nullable=False)
    problem_category = Column(String(50), nullable=False)
    problem_description = Column(Text, nullable=False)
    urgency_level = Column(String(20), nullable=False)
    user_id = Column(String(255), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), default=datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False,
    )
    status = Column(String(50), default="open", nullable=False)
    assigned_agent = Column(String(255), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    # Relationship
    conversation = relationship("ConversationModel", back_populates="support_tickets")

    data = Column(JSON, nullable=True)
