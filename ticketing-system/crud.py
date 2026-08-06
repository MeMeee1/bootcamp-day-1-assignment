from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Ticket, TicketMessage, TicketStatus


def get_all_tickets(db: Session) -> List[Ticket]:
    stmt = select(Ticket).order_by(Ticket.created_at.desc())
    return list(db.scalars(stmt).all())


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    stmt = (
        select(Ticket)
        .where(Ticket.ticket_id == ticket_id)
        .options(selectinload(Ticket.messages))
    )
    return db.scalar(stmt)


def create_ticket(db: Session, title: str, created_by: str) -> Ticket:
    ticket = Ticket(
        title=title,
        created_by=created_by,
        status=TicketStatus.OPEN,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket_id: int, status: TicketStatus) -> Optional[Ticket]:
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return None
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: int) -> bool:
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return False
    db.delete(ticket)
    db.commit()
    return True


def get_ticket_messages(db: Session, ticket_id: int) -> List[TicketMessage]:
    stmt = (
        select(TicketMessage)
        .where(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def add_message(db: Session, ticket_id: int, author: str, message_text: str) -> TicketMessage:
    message = TicketMessage(
        ticket_id=ticket_id,
        author=author,
        message_text=message_text,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def seed_sample_data(db: Session) -> bool:
    """
    Seed 3 tickets with 2 messages each if no tickets exist.
    Returns True if seeded, False if skipped.
    """
    existing = db.scalar(select(Ticket.ticket_id).limit(1))
    if existing is not None:
        return False

    tickets = [
        Ticket(title="Cannot login to dashboard", created_by="Alice", status=TicketStatus.OPEN),
        Ticket(title="Data sync job failed overnight", created_by="Bob", status=TicketStatus.IN_PROGRESS),
        Ticket(title="Feature request: export to CSV", created_by="Charlie", status=TicketStatus.RESOLVED),
    ]
    db.add_all(tickets)
    db.flush()

    messages = [
        TicketMessage(ticket_id=tickets[0].ticket_id, author="Alice", message_text="I get an invalid credentials error."),
        TicketMessage(ticket_id=tickets[0].ticket_id, author="Support", message_text="We are investigating your login issue."),
        TicketMessage(ticket_id=tickets[1].ticket_id, author="Bob", message_text="Job failed with timeout after 2 hours."),
        TicketMessage(ticket_id=tickets[1].ticket_id, author="Engineer", message_text="Increased cluster size and rerunning."),
        TicketMessage(ticket_id=tickets[2].ticket_id, author="Charlie", message_text="Need export option for reporting."),
        TicketMessage(ticket_id=tickets[2].ticket_id, author="Product", message_text="Implemented and released in v1.2."),
    ]
    db.add_all(messages)
    db.commit()
    return True
