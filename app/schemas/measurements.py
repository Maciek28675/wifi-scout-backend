from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class MeasurementBase(BaseModel):
    latitude: float = Field(
        ..., 
        ge=-90, 
        le=90,
        examples=[52.2297],
        description="Geographic latitude between -90 and 90 degrees"
    )
    longitude: float = Field(
        ..., 
        ge=-180, 
        le=180,
        examples=[21.0122],
        description="Geographic longitude between -180 and 180 degrees"
    )
    download_speed: Optional[float] = Field(
        None,
        ge=0,
        examples=[8.5],
        description="Download speed in Mbps"
    )
    upload_speed: Optional[float] = Field(
        None,
        ge=0,
        examples=[3.2],
        description="Upload speed in Mbps"
    )
    ping: Optional[int] = Field(
        None,
        gt=0,
        examples=[42],
        description="Network latency in milliseconds"
    )
    timestamp: Optional[datetime] = Field(
        None,
        examples=["2025-05-19T15:30:00"],
        description="Measurement timestamp in ISO 8601 format"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "latitude": 52.2297,
                "longitude": 21.0122,
                "signal_strength": -80,
                "download_speed": 8.5,
                "upload_speed": 3.2,
                "ping": 42,
                "timestamp": "2025-05-19T15:30:00"
            }
        }
    )

class MeasurementCreate(MeasurementBase):
    pass

class MeasurementUpdate(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    signal_strength: Optional[int] = Field(None, ge=-120, le=0)
    download_speed: Optional[float] = Field(None, ge=0)
    upload_speed: Optional[float] = Field(None, ge=0)
    ping: Optional[int] = Field(None, gt=0)
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "download_speed": 5.0,
                "ping": 60
            }
        }
    )

class MeasurementResponse(MeasurementBase):
    id: int = Field(..., examples=[1])
    color: str = Field(
        ..., 
        examples=["red"],
        description="Color indicator based on download speed (red/green/gray)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "latitude": 52.2297,
                "longitude": 21.0122,
                "signal_strength": -80,
                "download_speed": 8.5,
                "upload_speed": 3.2,
                "ping": 42,
                "timestamp": "2025-05-19T15:30:00",
                "color": "red"
            }
        }
    )
