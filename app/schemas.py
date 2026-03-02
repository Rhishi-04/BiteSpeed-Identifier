"""
Request/response shapes for the API (Pydantic). Same role as your usual schema modules.
"""
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class IdentifyRequest(BaseModel):
    """POST /identify body. At least one of email or phone_number required."""
    email: Optional[str] = None
    phoneNumber: Optional[str | int] = None  # API uses camelCase; accept number or string

    @field_validator("phoneNumber", mode="before")
    @classmethod
    def coerce_phone(cls, v):
        if v is None:
            return None
        return str(v).strip() or None

    @field_validator("email", mode="before")
    @classmethod
    def coerce_email(cls, v):
        if v is None:
            return None
        s = str(v).strip().lower()
        return s or None

    @model_validator(mode="after")
    def require_email_or_phone(self):
        if not self.email and not self.phoneNumber:
            raise ValueError("At least one of email or phoneNumber is required")
        return self


class ContactResponse(BaseModel):
    """Inner 'contact' object in the response (spec uses primaryContatctId typo)."""
    primaryContatctId: int
    emails: list[str]
    phoneNumbers: list[str]
    secondaryContactIds: list[int]


class IdentifyResponse(BaseModel):
    """Full response: { "contact": { ... } }."""
    contact: ContactResponse
