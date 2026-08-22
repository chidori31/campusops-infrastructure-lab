from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreate(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-zA-Z0-9._-]+$",
    )

    full_name: str = Field(
        min_length=2,
        max_length=255,
    )

    email: EmailStr

    department: str | None = Field(
        default=None,
        max_length=100,
    )


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    email: EmailStr | None = None

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    active: bool | None = None


class EmployeeRead(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    department: str | None
    active: bool
    ad_dn: str | None
    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DeviceCreate(BaseModel):
    hostname: str = Field(
        min_length=1,
        max_length=100,
    )

    serial_number: str | None = Field(
        default=None,
        max_length=100,
    )

    device_type: str = Field(
        min_length=2,
        max_length=50,
    )

    operating_system: str | None = Field(
        default=None,
        max_length=100,
    )

    status: str = Field(
        default="active",
        max_length=50,
    )

    ip_address: str | None = Field(
        default=None,
        max_length=45,
    )

    owner_id: int | None = None


class DeviceUpdate(BaseModel):
    serial_number: str | None = None
    operating_system: str | None = None
    status: str | None = None
    ip_address: str | None = None
    owner_id: int | None = None


class DeviceRead(BaseModel):
    id: int
    hostname: str
    serial_number: str | None
    device_type: str
    operating_system: str | None
    status: str
    ip_address: str | None
    owner_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TicketCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str = Field(
        min_length=5,
    )

    priority: str = Field(
        default="normal",
        pattern=r"^(low|normal|high|critical)$",
    )

    author_id: int
    assigned_to_id: int | None = None


class TicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
    )

    priority: str | None = Field(
        default=None,
        pattern=r"^(low|normal|high|critical)$",
    )

    status: str | None = Field(
        default=None,
        pattern=r"^(open|in_progress|resolved|closed)$",
    )

    assigned_to_id: int | None = None


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    author_id: int
    assigned_to_id: int | None
    created_at: datetime
    closed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )