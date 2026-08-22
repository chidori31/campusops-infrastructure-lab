from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Employee, Ticket
from app.schemas import (
    TicketCreate,
    TicketRead,
    TicketUpdate,
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


def require_employee(
    db: Session,
    employee_id: int,
    label: str,
) -> Employee:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=400,
            detail=f"{label} does not exist",
        )

    return employee


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
) -> Ticket:
    require_employee(
        db,
        payload.author_id,
        "Author",
    )

    if payload.assigned_to_id is not None:
        require_employee(
            db,
            payload.assigned_to_id,
            "Assigned employee",
        )

    ticket = Ticket(
        **payload.model_dump()
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.get(
    "",
    response_model=list[TicketRead],
)
def list_tickets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    priority: str | None = None,
    db: Session = Depends(get_db),
) -> list[Ticket]:
    statement = select(Ticket)

    if status_filter is not None:
        statement = statement.where(
            Ticket.status == status_filter
        )

    if priority is not None:
        statement = statement.where(
            Ticket.priority == priority
        )

    statement = (
        statement
        .order_by(Ticket.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = db.get(
        Ticket,
        ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketRead,
)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = db.get(
        Ticket,
        ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    data = payload.model_dump(
        exclude_unset=True
    )

    if (
        "assigned_to_id" in data
        and data["assigned_to_id"] is not None
    ):
        require_employee(
            db,
            data["assigned_to_id"],
            "Assigned employee",
        )

    old_status = ticket.status

    for field, value in data.items():
        setattr(
            ticket,
            field,
            value,
        )

    if (
        "status" in data
        and data["status"] in {"resolved", "closed"}
        and old_status not in {"resolved", "closed"}
    ):
        ticket.closed_at = datetime.now(
            timezone.utc
        )

    if (
        "status" in data
        and data["status"] in {"open", "in_progress"}
    ):
        ticket.closed_at = None

    db.commit()
    db.refresh(ticket)

    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> None:
    ticket = db.get(
        Ticket,
        ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    db.delete(ticket)
    db.commit()