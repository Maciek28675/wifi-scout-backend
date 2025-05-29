from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        comment="Optional reference to associated user"
    )
    latitude = Column(
        Float,
        CheckConstraint("latitude BETWEEN -90 AND 90"),
        nullable=False,
        comment="Geographic latitude (-90 to 90)"
    )
    longitude = Column(
        Float,
        CheckConstraint("longitude BETWEEN -180 AND 180"),
        nullable=False,
        comment="Geographic longitude (-180 to 180)"
    )
    height = Column(
        Float,
        CheckConstraint("height >= 0"),
        nullable=True,
        comment="Height above sea level in meters"
    )
    download_speed = Column(
        Float,
        CheckConstraint("download_speed >= 0"),
        nullable=True,
        comment="Download speed in Mbps"
    )
    upload_speed = Column(
        Float,
        CheckConstraint("upload_speed >= 0"),
        nullable=True,
        comment="Upload speed in Mbps"
    )
    ping = Column(
        Integer,
        CheckConstraint("ping > 0"),
        nullable=True,
        comment="Network latency in milliseconds"
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Measurement timestamp"
    )
    color = Column(
        String(5),
        CheckConstraint("color IN ('red', 'green', 'gray')"),
        nullable=False,
        comment="Color indicator based on speed thresholds"
    )

    user = relationship("User", back_populates="measurements")

    __table_args__ = (
        CheckConstraint("latitude IS NOT NULL AND longitude IS NOT NULL"),
    )
