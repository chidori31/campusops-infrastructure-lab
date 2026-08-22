from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    department: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    ad_dn: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        unique=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
        server_default="user",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    devices: Mapped[list["Device"]] = relationship(
        back_populates="owner",
    )

    created_tickets: Mapped[list["Ticket"]] = relationship(
        foreign_keys="Ticket.author_id",
        back_populates="author",
    )

    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        foreign_keys="Ticket.assigned_to_id",
        back_populates="assigned_to",
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)

    hostname: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    serial_number: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    device_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    operating_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    owner: Mapped[Employee | None] = relationship(
        back_populates="devices",
    )

    __table_args__ = (
        Index(
            "ix_devices_status_type",
            "status",
            "device_type",
        ),
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal",
        server_default="normal",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        server_default="open",
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    assigned_to_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    author: Mapped[Employee] = relationship(
        foreign_keys=[author_id],
        back_populates="created_tickets",
    )

    assigned_to: Mapped[Employee | None] = relationship(
        foreign_keys=[assigned_to_id],
        back_populates="assigned_tickets",
    )

    __table_args__ = (
        Index(
            "ix_tickets_status_priority",
            "status",
            "priority",
        ),
    )