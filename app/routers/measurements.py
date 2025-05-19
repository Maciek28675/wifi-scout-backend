from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud.measurement import MeasurementService
from app.db.database import get_db
from app.schemas.measurements import MeasurementBase, MeasurementResponse, MeasurementUpdate

router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"],
)

@router.post(
    "/",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Measurement successfully created"},
        400: {"description": "Missing required coordinates"},
        500: {"description": "Internal server error"}
    }
)
def create_measurement(measurement: MeasurementBase, db: Session = Depends(get_db)):
    service = MeasurementService(db)
    try:
        return service.create_measurement(measurement)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{measurement_id}",
    response_model=MeasurementResponse,
    responses={
        200: {"description": "Measurement found"},
        404: {"description": "Measurement not found"}
    }
)
def read_measurement(measurement_id: int, db: Session = Depends(get_db)):
    service = MeasurementService(db)
    measurement = service.get_measurement(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found"
        )
    return measurement

@router.get(
    "/",
    response_model=List[MeasurementResponse],
    description="Retrieve all measurements with pagination"
)
def read_measurements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = MeasurementService(db)
    return service.get_measurements(skip=skip, limit=limit)

@router.put(
    "/{measurement_id}",
    response_model=MeasurementResponse,
    responses={
        200: {"description": "Measurement updated"},
        404: {"description": "Measurement not found"}
    }
)
def update_measurement(
    measurement_id: int,
    measurement: MeasurementUpdate,
    db: Session = Depends(get_db)
):
    service = MeasurementService(db)
    updated = service.update_measurement(measurement_id, measurement)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found"
        )
    return updated

@router.delete(
    "/{measurement_id}",
    responses={
        200: {"description": "Measurement deleted"},
        404: {"description": "Measurement not found"}
    }
)
def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    service = MeasurementService(db)
    success = service.delete_measurement(measurement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found"
        )
    return {"message": "Pomiar usunięty"}
