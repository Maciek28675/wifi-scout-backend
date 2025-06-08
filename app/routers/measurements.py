import logging
from typing import List, Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session
from app.crud import MeasurementService
from app.db.database import get_db
from app.models import (
    Measurement,
)
from app.schemas import (
    MeasurementCreate,
    MeasurementResponse,
    MeasurementUpdate,
)
from app.utils.distance_utils import haversine_distance
from app.utils.buildings import find_building

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"],
)


@router.post("/", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement: MeasurementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Stwórz nowy pomiar."""
    service = MeasurementService(db)
    try:
        db_m = service.create_measurement(measurement)
        return MeasurementResponse.model_validate(db_m)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[create_measurement] {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Błąd serwera")


@router.get("/building")
async def get_building_name(
    latitude: float,
    longitude: float,
):
    """
    Zwraca nazwę budynku, jeśli podany punkt geograficzny znajduje się wewnątrz któregoś z budynków.
    """
    building = find_building(latitude, longitude)
    return {"building": building}


@router.get("/{measurement_id}", response_model=MeasurementResponse)
async def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Pobierz pomiar po ID."""
    service = MeasurementService(db)
    db_m = service.get_measurement(measurement_id)
    return MeasurementResponse.model_validate(db_m)


@router.get("/", response_model=List[MeasurementResponse])
async def list_measurements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    building_name: Optional[str] = Query(
        None, description="Filtruj po nazwie budynku"
    ),
    latitude: Optional[float] = Query(
        None, ge=-90, le=90, description="Szerokość geograficzna"
    ),
    longitude: Optional[float] = Query(
        None, ge=-180, le=180, description="Długość geograficzna"
    ),
    radius_km: float = Query(1.0, gt=0, description="Promień wyszukiwania w km"),
    db: Session = Depends(get_db),
):
    """
    Pobierz:
     - agregaty dla `building_name`, lub
     - pobliskie punkty w promieniu `radius_km` od (latitude, longitude).
    """
    service = MeasurementService(db)
    result = service.get_measurements(
        skip, limit, building_name, latitude, longitude, radius_km
    )

    if result and isinstance(result[0], dict):
        return [MeasurementResponse.model_validate(m) for m in result]  # z distance_m
    
    return [MeasurementResponse.model_validate(m) for m in result]  # z sumami, count i avg


@router.put("/{measurement_id}", response_model=MeasurementResponse)
async def update_measurement(
    measurement_id: int,
    measurement_update: MeasurementUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Zaktualizuj istniejący agregat pomiarów."""
    service = MeasurementService(db)
    try:
        db_m = service.update_measurement(measurement_id, measurement_update)
        return MeasurementResponse.model_validate(db_m)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[update_measurement] {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Błąd serwera")



@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Usuń agregat pomiarów."""
    service = MeasurementService(db)
    try:
        service.delete_measurement(measurement_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[delete_measurement] {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Błąd serwera")

