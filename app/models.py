"""
Contact table: one row per collected email/phone. Primary vs secondary linked by linked_id.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linked_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)  # primary contact's id
    link_precedence = Column(String, nullable=False)  # "primary" or "secondary"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Self-relation: secondary contacts point to primary
    primary_contact = relationship("Contact", remote_side=[id], backref="secondary_contacts")
