from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Device, Employee
from app.schemas import (
    DeviceCreate,
    DeviceRead,
    DeviceUpdate,
)


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post(
    "",
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
) -> Device:
    if payload.owner_id is not None:
        owner = db.get(
            Employee,
            payload.owner_id,
        )

        if owner is None:
            raise HTTPException(
                status_code=400,
                detail="Owner does not exist",
            )

    device = Device(
        **payload.model_dump()
    )

    db.add(device)

    try:
        db.commit()
        db.refresh(device)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Hostname or serial number already exists",
        ) from exc

    return device


@router.get(
    "",
    response_model=list[DeviceRead],
)
def list_devices(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    device_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[Device]:
    statement = select(Device)

    if status_filter is not None:
        statement = statement.where(
            Device.status == status_filter
        )

    if device_type is not None:
        statement = statement.where(
            Device.device_type == device_type
        )

    statement = (
        statement
        .order_by(Device.id)
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/{device_id}",
    response_model=DeviceRead,
)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
) -> Device:
    device = db.get(
        Device,
        device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return device


@router.patch(
    "/{device_id}",
    response_model=DeviceRead,
)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
) -> Device:
    device = db.get(
        Device,
        device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    data = payload.model_dump(
        exclude_unset=True
    )

    if (
        "owner_id" in data
        and data["owner_id"] is not None
    ):
        owner = db.get(
            Employee,
            data["owner_id"],
        )

        if owner is None:
            raise HTTPException(
                status_code=400,
                detail="Owner does not exist",
            )

    for field, value in data.items():
        setattr(
            device,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(device)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Device update conflicts with existing record",
        ) from exc

    return device


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
) -> None:
    device = db.get(
        Device,
        device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    db.delete(device)
    db.commit()