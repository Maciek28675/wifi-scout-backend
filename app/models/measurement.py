from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    text,
    Computed,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class MeasurementAggregate(Base):
    """Agregacja pomiarów dla pobliskich lokalizacji"""

    __tablename__ = "measurement_aggregates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(
        String(50), ForeignKey("measurement_zones.zone_id"), nullable=False
    )
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)

    measurement_count = Column(Integer, nullable=False, default=1)
    download_speed_sum = Column(Float, default=0)
    download_speed_avg = Column(Float, default=0)
    download_speed_min = Column(Float)
    download_speed_max = Column(Float)
    upload_speed_sum = Column(Float, default=0)
    upload_speed_avg = Column(Float, default=0)
    upload_speed_min = Column(Float)
    upload_speed_max = Column(Float)
    ping_sum = Column(Integer, default=0)
    ping_avg = Column(Float, default=0)
    ping_min = Column(Integer)
    ping_max = Column(Integer)
    first_measurement = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_measurement = Column(DateTime, nullable=False, default=datetime.utcnow)
    color = Column(
        String(5),
        Computed(
            """
            CASE 
                WHEN download_speed_avg IS NULL THEN 'gray'
                WHEN download_speed_avg < 10 THEN 'red'
                ELSE 'green'
            END
        """
        ),
        nullable=False,
    )

    zone = relationship("MeasurementZone", back_populates="aggregates")
    measurements = relationship("Measurement", back_populates="aggregate")

    __table_args__ = (
        Index("idx_agg_zone_id", "zone_id"),
        Index("idx_agg_center_coords", "center_latitude", "center_longitude"),
        Index("idx_agg_last_measurement", "last_measurement"),
        Index(
            "unique_zone_aggregate",
            "zone_id",
            "center_latitude",
            "center_longitude",
            unique=True,
        ),
    )


class MeasurementZone(Base):
    """Pomiar dla określonego obszaru geograficznego"""

    __tablename__ = "measurement_zones"

    zone_id = Column(String(50), primary_key=True)
    min_latitude = Column(Float, nullable=False)
    max_latitude = Column(Float, nullable=False)
    min_longitude = Column(Float, nullable=False)
    max_longitude = Column(Float, nullable=False)

    total_measurements = Column(Integer, default=0)
    total_aggregates = Column(Integer, default=0)
    avg_measurements_per_aggregate = Column(Float, default=0)
    zone_avg_download = Column(Float)
    zone_avg_upload = Column(Float)
    zone_avg_ping = Column(Float)
    first_measurement = Column(DateTime)
    last_measurement = Column(DateTime)

    aggregates = relationship("MeasurementAggregate", back_populates="zone")
    measurements = relationship("Measurement", back_populates="zone")

    __table_args__ = (
        Index(
            "idx_zone_bounds",
            "min_latitude",
            "max_latitude",
            "min_longitude",
            "max_longitude",
        ),
    )


class Measurement(Base):
    """Pomiar prędkości internetu i lokalizacji"""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Optional reference to associated user",
    )

    latitude = Column(
        Float,
        CheckConstraint("latitude BETWEEN -90 AND 90"),
        nullable=False,
        comment="Geographic latitude (-90 to 90)",
    )
    longitude = Column(
        Float,
        CheckConstraint("longitude BETWEEN -180 AND 180"),
        nullable=False,
        comment="Geographic longitude (-180 to 180)",
    )
    height = Column(
        Float,
        CheckConstraint("height >= 0"),
        nullable=True,
        comment="Height above sea level in meters",
    )

    download_speed = Column(
        Float,
        CheckConstraint("download_speed >= 0"),
        nullable=True,
        comment="Download speed in Mbps",
    )
    upload_speed = Column(
        Float,
        CheckConstraint("upload_speed >= 0"),
        nullable=True,
        comment="Upload speed in Mbps",
    )
    ping = Column(
        Integer,
        CheckConstraint("ping > 0"),
        nullable=True,
        comment="Network latency in milliseconds",
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Measurement timestamp",
    )
    color = Column(
        String(5),
        CheckConstraint("color IN ('red', 'green', 'gray')"),
        nullable=False,
        comment="Color indicator based on speed thresholds",
    )
    zone_id = Column(
        String(50), ForeignKey("measurement_zones.zone_id"), nullable=False
    )
    geohash = Column(String(12))  # Dodatkowe indeksowanie geohash
    aggregate_id = Column(Integer, ForeignKey("measurement_aggregates.id"))

    user = relationship("User", back_populates="measurements")
    zone = relationship("MeasurementZone", back_populates="measurements")
    aggregate = relationship("MeasurementAggregate", back_populates="measurements")

    __table_args__ = (
        CheckConstraint("latitude IS NOT NULL AND longitude IS NOT NULL"),
        Index("idx_zone_id", "zone_id"),
        Index("idx_geohash", "geohash"),
        Index("idx_aggregate_id", "aggregate_id"),
        Index("idx_coordinates", "latitude", "longitude"),
        Index("idx_timestamp", "timestamp"),
        Index("idx_zone_timestamp", "zone_id", "timestamp"),
    )
