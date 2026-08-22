from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Employee
from app.schemas import (
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
) -> Employee:
    employee = Employee(
        username=payload.username,
        full_name=payload.full_name,
        email=str(payload.email),
        department=payload.department,
    )

    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        ) from exc

    return employee


@router.get(
    "",
    response_model=list[EmployeeRead],
)
def list_employees(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    department: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Employee]:
    statement = select(Employee)

    if department is not None:
        statement = statement.where(
            Employee.department == department
        )

    if active is not None:
        statement = statement.where(
            Employee.active == active
        )

    statement = (
        statement
        .order_by(Employee.id)
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
) -> Employee:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return employee


@router.patch(
    "/{employee_id}",
    response_model=EmployeeRead,
)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
) -> Employee:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    data = payload.model_dump(
        exclude_unset=True
    )

    if "email" in data and data["email"] is not None:
        data["email"] = str(data["email"])

    for field, value in data.items():
        setattr(
            employee,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee data conflicts with existing record",
        ) from exc

    return employee


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
) -> None:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    db.delete(employee)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Employee cannot be deleted while "
                "referenced by another object"
            ),
        ) from exc