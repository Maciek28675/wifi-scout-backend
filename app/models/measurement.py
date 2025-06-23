from datetime import datetime, timezone
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
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Measurement(Base):
    """Zagregowany pomiar prędkości internetu i lokalizacji"""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Optional reference to associated user for this aggregated point",
    )

    latitude = Column(
        Float,
        CheckConstraint("latitude BETWEEN -90 AND 90"),
        nullable=False,
        comment="Geographic latitude of the aggregated point (-90 to 90)",
    )
    longitude = Column(
        Float,
        CheckConstraint("longitude BETWEEN -180 AND 180"),
        nullable=False,
        comment="Geographic longitude of the aggregated point (-180 to 180)",
    )
    height = Column(
        Float,
        CheckConstraint("height >= 0"),
        nullable=True,
        comment="Average height above sea level in meters for aggregated measurements",
    )

    download_speed = Column(
        Float,
        CheckConstraint("download_speed >= 0"),
        nullable=True,
        comment="Average download speed in Mbps",
    )
    upload_speed = Column(
        Float,
        CheckConstraint("upload_speed >= 0"),
        nullable=True,
        comment="Average upload speed in Mbps",
    )
    ping = Column(
        Integer,
        CheckConstraint("ping > 0"),
        nullable=True,
        comment="Average network latency in milliseconds",
    )

    download_speed_sum = Column(
        Float,
        nullable=False,
        server_default=text("0.0"),
        comment="Sum of download speeds in Mbps for all measurements at this point",
    )
    upload_speed_sum = Column(
        Float,
        nullable=False,
        server_default=text("0.0"),
        comment="Sum of upload speeds in Mbps for all measurements at this point",
    )
    ping_sum = Column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Sum of pings in milliseconds for all measurements at this point",
    )
    measurement_count = Column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Number of individual measurements aggregated at this point",
    )

    building_name = Column(
        String,
        nullable=True,
        comment="Name of the building, if applicable"
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.now(timezone.utc), 
        comment="Timestamp of the last update or last measurement included in the aggregate",
    )
    color = Column(
        String(7),
        nullable=False,
        comment="Color indicator based on average download speed thresholds",
    )
   
    user = relationship("User", back_populates="measurements")

    __table_args__ = (
        CheckConstraint("latitude IS NOT NULL AND longitude IS NOT NULL"),
        Index("idx_coordinates", "latitude", "longitude"),
        Index("idx_timestamp", "timestamp"),
        Index("idx_building_name", "building_name"),
    )