"""
POST /identify: receive email/phone, return consolidated contact.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IdentifyRequest, IdentifyResponse
from app import identify_service

router = APIRouter()


@router.post("", response_model=IdentifyResponse)
def identify_endpoint(body: IdentifyRequest, db: Session = Depends(get_db)):
    """Create or link contacts and return the consolidated contact."""
    try:
        return identify_service.identify(db, body.email, body.phoneNumber)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
