from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer
from typing import Optional, Dict, Any
from datetime import datetime
import re


class MeasurementBase(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        examples=[52.2297],
        description="Geographic latitude between -90 and 90 degrees",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        examples=[21.0122],
        description="Geographic longitude between -180 and 180 degrees",
    )
    height: Optional[float] = Field(
        None, ge=0, examples=[100.0], description="Height above sea level in meters"
    )
    download_speed: Optional[float] = Field(
        None, ge=0, examples=[8.5], description="Download speed in Mbps"
    )
    upload_speed: Optional[float] = Field(
        None, ge=0, examples=[3.2], description="Upload speed in Mbps"
    )
    ping: Optional[int] = Field(
        None, gt=0, examples=[42], description="Network latency in milliseconds"
    )
    timestamp: Optional[datetime] = Field(
        None,
        examples=["2025-05-19T15:30:00"],
        description="Measurement timestamp in ISO 8601 format",
    )
    zone_id: Optional[str] = Field(
        None,
        max_length=50,
        pattern=r"^zone_-?\d+_-?\d+$",
        examples=["zone_52_21"],
        description="Zone identifier for spatial partitioning",
    )
    geohash: Optional[str] = Field(
        None,
        max_length=12,
        examples=["u3k2b9f8h"],
        description="Geohash for spatial indexing",
    )
    aggregate_id: Optional[int] = Field(
        None, gt=0, examples=[123], description="Reference to measurement aggregate"
    )

    @field_validator("zone_id", mode="before")
    @classmethod
    def validate_zone_id(cls, v: Any) -> Optional[str]:
        """Waliduj format zone_id"""
        if v is None:
            return None
        if isinstance(v, str) and re.match(r"^zone_-?\d+_-?\d+$", v):
            return v
        raise ValueError("zone_id musi być w formacie 'zone_<lat_cell>_<lon_cell>'")

    @field_validator("geohash", mode="before")
    @classmethod
    def validate_geohash(cls, v: Any) -> Optional[str]:
        """Waliduj format geohash"""
        if v is None:
            return None
        if isinstance(v, str) and len(v) <= 12 and v.isalnum():
            return v
        raise ValueError("Invalid geohash format")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "latitude": 52.2297,
                "longitude": 21.0122,
                "height": 100.0,
                "download_speed": 8.5,
                "upload_speed": 3.2,
                "ping": 42,
                "timestamp": "2025-05-19T15:30:00",
                "zone_id": "zone_52_21",
                "geohash": "u3k2b9f8h",
                "aggregate_id": 123,
            }
        },
    )


class MeasurementCreate(MeasurementBase):
    """Schema dla tworzenia nowych pomiarów"""

    pass


class MeasurementUpdate(BaseModel):
    """Schema dla aktualizacji pomiarów"""

    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    height: Optional[float] = Field(None, ge=0)
    download_speed: Optional[float] = Field(None, ge=0)
    upload_speed: Optional[float] = Field(None, ge=0)
    ping: Optional[int] = Field(None, gt=0)
    timestamp: Optional[datetime] = None
    zone_id: Optional[str] = Field(None, max_length=50, pattern=r"^zone_-?\d+_-?\d+$")
    geohash: Optional[str] = Field(None, max_length=12)
    aggregate_id: Optional[int] = Field(None, gt=0)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"download_speed": 5.0, "ping": 60, "zone_id": "zone_52_21"}
        },
    )


class MeasurementResponse(MeasurementBase):
    """Schema dla odpowiedzi na pomiar"""

    id: int = Field(..., examples=[1])
    color: str = Field(
        ...,
        examples=["red"],
        description="Color indicator based on download speed (red/green/gray)",
    )
    zone_id: str = Field(..., description="Zone identifier")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "latitude": 52.2297,
                "longitude": 21.0122,
                "height": 100.0,
                "download_speed": 8.5,
                "upload_speed": 3.2,
                "ping": 42,
                "timestamp": "2025-05-19T15:30:00",
                "color": "red",
                "zone_id": "zone_52_21",
                "geohash": "u3k2b9f8h",
                "aggregate_id": 123,
            }
        },
    )


class MeasurementAggregateResponse(BaseModel):
    """Schema dla agregatów pomiarów"""

    id: int
    zone_id: str
    center_latitude: float
    center_longitude: float
    measurement_count: int
    download_speed_avg: Optional[float]
    upload_speed_avg: Optional[float]
    ping_avg: Optional[float]
    first_measurement: datetime
    last_measurement: datetime
    color: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "zone_id": "zone_52_21",
                "center_latitude": 52.2297,
                "center_longitude": 21.0122,
                "measurement_count": 5,
                "download_speed_avg": 8.5,
                "upload_speed_avg": 3.2,
                "ping_avg": 42.0,
                "first_measurement": "2025-05-19T15:30:00",
                "last_measurement": "2025-05-19T16:30:00",
                "color": "red",
            }
        },
    )


class CoordinateResponse(BaseModel):
    """Simple response for coordinate data"""

    latitude: float
    longitude: float

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "latitude": 52.2297,
                "longitude": 21.0122,
            }
        },
    )


class DistanceResponse(BaseModel):
    """Response for distance calculations"""

    distance_meters: float
    distance_km: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "distance_meters": 1500.0,
                "distance_km": 1.5,
            }
        },
    )
