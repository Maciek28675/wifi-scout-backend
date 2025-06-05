from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


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
    building_name: Optional[str] = Field(
        None,  
        examples=["Building A"],
        description="Name of the building where the measurement was taken",
    )

    model_config = ConfigDict(from_attributes=True)



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
    building_name: Optional[str] = Field(
        None,
        examples=["Building A"],
        description="Name of the building where the measurement was taken",
    )
    download_speed_sum: Optional[float] = Field(
        None, description="Sum of download speeds for aggregated measurements"
    )
    upload_speed_sum: Optional[float] = Field(
        None, description="Sum of upload speeds for aggregated measurements"
    )
    ping_sum: Optional[int] = Field(
        None, description="Sum of ping values for aggregated measurements"
    )
    measurement_count: Optional[int] = Field(
        None, description="Number of measurements aggregated at this point"
    )
    model_config = ConfigDict(from_attributes=True)



class MeasurementResponse(MeasurementBase):
    """Schema dla odpowiedzi na pomiar"""

    id: int = Field(..., examples=[1])

    # Sumy
    download_speed_sum: float = Field(..., description="Sum of download speeds")
    upload_speed_sum: float = Field(..., description="Sum of upload speeds")
    ping_sum: int = Field(..., description="Sum of ping values")
    measurement_count: int = Field(..., description="Number of measurements aggregated")

    # Średnie
    download_speed: Optional[float] = Field(
        None, description="Average download speed (sum/count)"
    )
    upload_speed: Optional[float] = Field(
        None, description="Average upload speed (sum/count)"
    )
    ping: Optional[int] = Field(
        None, description="Average ping (sum/count)"
    )

    color: str = Field(
        ...,
        examples=["red"],
        description="Color indicator based on download speed (red/green/gray)",
    )
    timestamp: datetime = Field(..., description="Last update timestamp")
    model_config = ConfigDict(from_attributes=True)
