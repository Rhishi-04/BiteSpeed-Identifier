"""
Identify logic: find or create contacts, link primary/secondary, return consolidated view.
"""
from sqlalchemy.orm import Session
from app.models import Contact
from app.schemas import IdentifyResponse


def _normalize_email(v: str | int | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip().lower()
    return s or None


def _normalize_phone(v: str | int | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _build_response(
    primary_id: int,
    contacts: list[Contact],
    secondary_ids: list[int],
) -> IdentifyResponse:
    """Build API response: primary first in emails/phones, then secondaries, deduplicated."""
    primary = next(c for c in contacts if c.id == primary_id)
    emails: list[str] = []
    phones: list[str] = []
    seen_e: set[str] = set()
    seen_p: set[str] = set()

    if primary.email and primary.email not in seen_e:
        emails.append(primary.email)
        seen_e.add(primary.email)
    if primary.phone_number and primary.phone_number not in seen_p:
        phones.append(primary.phone_number)
        seen_p.add(primary.phone_number)

    for c in contacts:
        if c.id == primary_id:
            continue
        if c.email and c.email not in seen_e:
            emails.append(c.email)
            seen_e.add(c.email)
        if c.phone_number and c.phone_number not in seen_p:
            phones.append(c.phone_number)
            seen_p.add(c.phone_number)

    return IdentifyResponse(
        contact={
            "primaryContatctId": primary_id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids,
        }
    )


def identify(
    db: Session,
    email: str | int | None,
    phone_number: str | int | None,
) -> IdentifyResponse:
    """
    1. If no contact matches email/phone -> create new primary, return it.
    2. If one chain matches -> optionally create secondary if new info; return consolidated.
    3. If two primaries match (e.g. email from one, phone from other) -> merge (newer becomes secondary).
    """
    em = _normalize_email(email)
    ph = _normalize_phone(phone_number)

    if not em and not ph:
        raise ValueError("At least one of email or phoneNumber is required")

    # 1) Find all contacts matching this email or phone
    from sqlalchemy import or_

    conditions = []
    if em:
        conditions.append(Contact.email == em)
    if ph:
        conditions.append(Contact.phone_number == ph)

    candidates = (
        db.query(Contact)
        .filter(or_(*conditions), Contact.deleted_at.is_(None))
        .order_by(Contact.created_at.asc())
        .all()
    )

    if not candidates:
        # New customer: create primary
        primary = Contact(
            email=em,
            phone_number=ph,
            link_precedence="primary",
        )
        db.add(primary)
        db.commit()
        db.refresh(primary)
        return _build_response(primary.id, [primary], [])

    # 2) Resolve primary id for each candidate
    primary_ids = set()
    for c in candidates:
        root_id = c.id if c.link_precedence == "primary" else (c.linked_id or c.id)
        primary_ids.add(root_id)

    primaries = (
        db.query(Contact)
        .filter(Contact.id.in_(primary_ids), Contact.deleted_at.is_(None))
        .order_by(Contact.created_at.asc())
        .all()
    )
    oldest_primary = primaries[0]
    primary_id = oldest_primary.id

    # 3) If two primaries, merge: newer ones become secondary
    if len(primaries) > 1:
        for p in primaries[1:]:
            p.linked_id = primary_id
            p.link_precedence = "secondary"
        # Point any secondaries of the old primaries to the chosen primary
        for p in primaries[1:]:
            db.query(Contact).filter(Contact.linked_id == p.id).update(
                {"linked_id": primary_id}
            )
        db.commit()

    # 4) All contacts in the chain (primary + secondaries)
    all_in_chain = (
        db.query(Contact)
        .filter(
            (Contact.id == primary_id) | (Contact.linked_id == primary_id),
            Contact.deleted_at.is_(None),
        )
        .order_by(Contact.created_at.asc())
        .all()
    )

    primary_contact = next(c for c in all_in_chain if c.id == primary_id)
    secondaries = [c for c in all_in_chain if c.id != primary_id]

    # 5) Create new secondary if request has new email or phone
    existing_emails = {c.email for c in all_in_chain if c.email}
    existing_phones = {c.phone_number for c in all_in_chain if c.phone_number}
    has_new_email = em and em not in existing_emails
    has_new_phone = ph and ph not in existing_phones

    if has_new_email or has_new_phone:
        new_contact = Contact(
            email=em,
            phone_number=ph,
            linked_id=primary_id,
            link_precedence="secondary",
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        secondaries.append(new_contact)

    all_contacts = [primary_contact] + secondaries
    secondary_ids = [c.id for c in all_contacts if c.link_precedence == "secondary"]

    return _build_response(primary_id, all_contacts, secondary_ids)
