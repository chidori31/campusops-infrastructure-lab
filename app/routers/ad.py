from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Employee
from app.services.active_directory import (
    ActiveDirectoryUnavailable,
    ActiveDirectoryUserNotFound,
    check_active_directory,
    get_active_directory_user,
)


router = APIRouter(
    prefix="/ad",
    tags=["Active Directory"],
)


@router.get("/status")
def ad_status():
    try:
        return check_active_directory()

    except ActiveDirectoryUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.get("/users/{username}")
def get_ad_user(
    username: str,
):
    try:
        user = get_active_directory_user(
            username
        )

    except ActiveDirectoryUserNotFound as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ActiveDirectoryUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "distinguished_name": user.distinguished_name,
        "groups": user.groups,
        "role": user.role,
    }


@router.post("/sync/{username}")
def sync_ad_user(
    username: str,
    db: Session = Depends(get_db),
):
    try:
        ad_user = get_active_directory_user(
            username
        )

    except ActiveDirectoryUserNotFound as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ActiveDirectoryUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    employee = db.scalar(
        select(Employee).where(
            Employee.username
            == ad_user.username
        )
    )

    created = employee is None

    if employee is None:
        employee = Employee(
            username=ad_user.username,
            full_name=ad_user.full_name,
            email=ad_user.email,
            department=None,
            active=True,
            ad_dn=ad_user.distinguished_name,
            role=ad_user.role,
        )

        db.add(employee)

    else:
        employee.full_name = ad_user.full_name
        employee.email = ad_user.email
        employee.ad_dn = ad_user.distinguished_name
        employee.role = ad_user.role
        employee.active = True

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Active Directory user conflicts "
                "with existing employee data"
            ),
        ) from exc

    return {
        "created": created,
        "employee_id": employee.id,
        "username": employee.username,
        "role": employee.role,
        "ad_dn": employee.ad_dn,
        "groups": ad_user.groups,
    }