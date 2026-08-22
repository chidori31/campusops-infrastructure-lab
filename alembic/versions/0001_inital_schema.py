"""Initial CampusOps schema.

Revision ID: 0001
Revises:
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "department",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "ad_dn",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "role",
            sa.String(length=50),
            server_default=sa.text("'user'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "username",
            name="uq_employees_username",
        ),
        sa.UniqueConstraint(
            "email",
            name="uq_employees_email",
        ),
        sa.UniqueConstraint(
            "ad_dn",
            name="uq_employees_ad_dn",
        ),
    )

    op.create_index(
        "ix_employees_username",
        "employees",
        ["username"],
    )

    op.create_index(
        "ix_employees_department",
        "employees",
        ["department"],
    )

    op.create_table(
        "devices",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "hostname",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "serial_number",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "device_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "operating_system",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=True,
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["employees.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "hostname",
            name="uq_devices_hostname",
        ),
        sa.UniqueConstraint(
            "serial_number",
            name="uq_devices_serial_number",
        ),
    )

    op.create_index(
        "ix_devices_hostname",
        "devices",
        ["hostname"],
    )

    op.create_index(
        "ix_devices_status_type",
        "devices",
        ["status", "device_type"],
    )

    op.create_table(
        "tickets",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.String(length=20),
            server_default=sa.text("'normal'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'open'"),
            nullable=False,
        ),
        sa.Column(
            "author_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "assigned_to_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["employees.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to_id"],
            ["employees.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_tickets_status_priority",
        "tickets",
        ["status", "priority"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tickets_status_priority",
        table_name="tickets",
    )
    op.drop_table("tickets")

    op.drop_index(
        "ix_devices_status_type",
        table_name="devices",
    )
    op.drop_index(
        "ix_devices_hostname",
        table_name="devices",
    )
    op.drop_table("devices")

    op.drop_index(
        "ix_employees_department",
        table_name="employees",
    )
    op.drop_index(
        "ix_employees_username",
        table_name="employees",
    )
    op.drop_table("employees")