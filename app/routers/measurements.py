import logging
from typing import List, Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session
from app.crud import MeasurementService
from app.db.database import get_db
from app.models import (
    Measurement,
    MeasurementAggregate,
    MeasurementZone,
)
from app.schemas import (
    MeasurementAggregateResponse,
    MeasurementCreate,
    MeasurementResponse,
    MeasurementUpdate,
    CoordinateResponse,
    DistanceResponse,
)
from app.utils.distance_utils import haversine_distance

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"],
)


def update_zone_stats(db: Session, zone_id: str):
    """Zaktualizuje statystyki strefy po zmianie pomiaru."""
    try:
        measurement_service = MeasurementService(db)
        measurement_service.update_zone_statistics(zone_id)
        logger.info(f"Zaktualizowano statystyki strefy: {zone_id}")
    except Exception as e:
        logger.error(f"Error podczas aktualizacji statystyk strefy {zone_id}: {e}")


@router.post("/", response_model=MeasurementResponse)
async def create_measurement(
    measurement: MeasurementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Stwórz nowy pomiar."""
    try:
        service = MeasurementService(db)
        db_measurement = service.create_measurement(measurement)

        # Update zone statistics in background
        if db_measurement.zone_id:
            background_tasks.add_task(update_zone_stats, db, db_measurement.zone_id)

        return MeasurementResponse.model_validate(db_measurement)

    except Exception as e:
        logger.error(f"Błąd podczas tworzenia pomiaru: {e}")
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera")


@router.get("/{measurement_id}", response_model=MeasurementResponse)
async def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Pobierz pomiar po ID."""
    service = MeasurementService(db)
    db_measurement = service.get_measurement(measurement_id)
    return MeasurementResponse.model_validate(db_measurement)


@router.get("/", response_model=List[MeasurementResponse])
async def get_measurements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    zone_id: Optional[str] = Query(None, pattern=r"^zone_-?\d+_-?\d+$"),
    min_speed: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """
    Pobierz pomiary z opcjonalnym filtrowaniem.

    Args:
        - `skip`: Liczba pomiarów do pominięcia (stronicowanie).
        - `limit`: Maksymalna liczba pomiarów do zwrócenia.
        - `zone_id`: Opcjonalne ID strefy do filtrowania pomiarów.
        - `min_speed`: Minimalna prędkość pobierania do filtrowania pomiarów.

    Returns:
        - Lista pomiarów spełniających kryteria filtrowania.
    """
    query = db.query(Measurement)

    if zone_id:
        query = query.filter(Measurement.zone_id == zone_id)

    if min_speed is not None:
        query = query.filter(Measurement.download_speed >= min_speed)

    measurements = query.offset(skip).limit(limit).all()
    return [MeasurementResponse.model_validate(m) for m in measurements]


@router.put("/{measurement_id}", response_model=MeasurementResponse)
async def update_measurement(
    measurement_id: int,
    measurement_update: MeasurementUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Zaaktualizuj pomiar."""
    service = MeasurementService(db)

    # Pobierz oryginalny pomiar, aby sprawdzić strefę
    original_measurement = service.get_measurement(measurement_id)
    original_zone_id = original_measurement.zone_id

    db_measurement = service.update_measurement(measurement_id, measurement_update)

    # Uaktualizuj statystyki strefy w tle dla bieżącej i oryginalnej strefy
    current_zone_id = db_measurement.zone_id
    if current_zone_id:
        background_tasks.add_task(update_zone_stats, db, current_zone_id)

    if original_zone_id and original_zone_id != current_zone_id:
        background_tasks.add_task(update_zone_stats, db, original_zone_id)

    return MeasurementResponse.model_validate(db_measurement)


@router.delete("/{measurement_id}")
async def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Usunięcie pomiaru."""
    service = MeasurementService(db)

    # Pobierz pomiar, aby sprawdzić strefę do aktualizacji statystyk
    measurement = service.get_measurement(measurement_id)
    zone_id_to_update = measurement.zone_id

    result = service.delete_measurement(measurement_id)

    if zone_id_to_update:
        service.update_zone_statistics(zone_id_to_update)

    return result


@router.get(
    "/nearby",
    response_model=List[MeasurementResponse],
    responses={
        200: {"description": "Znaleziono pomiary w pobliżu"},
        404: {"description": "Nie znaleziono pomiarów w pobliżu"},
        500: {"description": "Wewnętrzny błąd serwera"},
    },
)
def read_measurements_nearby(
    latitude: float = Query(..., description="Szerokość geograficzna"),
    longitude: float = Query(..., description="Długość geograficzna"),
    radius_km: float = Query(1.0, description="Promień w km"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Pobierz pomiary w pobliżu określonej lokalizacji."""
    service = MeasurementService(db)
    measurements = service.get_measurements_nearby(
        latitude, longitude, radius_km, skip, limit
    )
    return [MeasurementResponse.model_validate(m) for m in measurements]


@router.get("/aggregates/", response_model=List[MeasurementAggregateResponse])
async def get_measurement_aggregates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    zone_id: Optional[str] = Query(None, pattern=r"^zone_-?\d+_-?\d+$"),
    min_measurements: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """Zwróć agregaty pomiarów z opcjonalnym filtrowaniem."""
    query = db.query(MeasurementAggregate)

    if zone_id:
        query = query.filter(MeasurementAggregate.zone_id == zone_id)

    if min_measurements is not None:
        query = query.filter(MeasurementAggregate.measurement_count >= min_measurements)

    aggregates = query.offset(skip).limit(limit).all()
    return [MeasurementAggregateResponse.model_validate(agg) for agg in aggregates]


@router.get("/zones/{zone_id}/stats")
async def get_zone_statistics(zone_id: str, db: Session = Depends(get_db)):
    """Zwróć statystyki strefy pomiarowej."""
    zone = db.query(MeasurementZone).filter(MeasurementZone.zone_id == zone_id).first()

    if not zone:
        raise HTTPException(status_code=404, detail="Strefa nie znaleziona")

    return {
        "zone_id": zone.zone_id,
        "total_measurements": zone.total_measurements,
        "total_aggregates": zone.total_aggregates,
        "avg_measurements_per_aggregate": zone.avg_measurements_per_aggregate,
        "zone_avg_download": zone.zone_avg_download,
        "zone_avg_upload": zone.zone_avg_upload,
        "zone_avg_ping": zone.zone_avg_ping,
        "first_measurement": zone.first_measurement,
        "last_measurement": zone.last_measurement,
        "bounds": {
            "min_latitude": zone.min_latitude,
            "max_latitude": zone.max_latitude,
            "min_longitude": zone.min_longitude,
            "max_longitude": zone.max_longitude,
        },
    }


@router.post("/distance", response_model=DistanceResponse)
async def calculate_distance(
    lat1: float = Query(..., description="Pierwsza szerokość geograficzna"),
    lon1: float = Query(..., description="Pierwsza długość geograficzna"),
    lat2: float = Query(..., description="Druga szerokość geograficzna"),
    lon2: float = Query(..., description="Druga długość geograficzna"),
):
    """Oblicz odległość między dwoma punktami."""
    try:
        distance_meters = haversine_distance(lat1, lon1, lat2, lon2)
        distance_km = distance_meters / 1000.0

        return DistanceResponse(
            distance_meters=distance_meters, distance_km=distance_km
        )
    except Exception as e:
        logger.error(f"Error podczas obliczania odległości: {e}")
        raise HTTPException(
            status_code=500, detail="Błąd podczas obliczania odległości"
        )


@router.get("/zones/", response_model=List[dict])
async def get_zones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Pobierz listę stref pomiarowych."""
    zones = db.query(MeasurementZone).offset(skip).limit(limit).all()

    return [
        {
            "zone_id": zone.zone_id,
            "total_measurements": zone.total_measurements,
            "bounds": {
                "min_latitude": zone.min_latitude,
                "max_latitude": zone.max_latitude,
                "min_longitude": zone.min_longitude,
                "max_longitude": zone.max_longitude,
            },
            "avg_download": zone.zone_avg_download,
            "avg_upload": zone.zone_avg_upload,
            "avg_ping": zone.zone_avg_ping,
        }
        for zone in zones
    ]
