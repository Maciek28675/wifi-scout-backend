from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.measurement import Measurement
from app.schemas.measurements import MeasurementBase, MeasurementUpdate
from datetime import datetime
from math import radians, cos, sin, asin, sqrt


class MeasurementService:
    def __init__(self, db: Session):
        self.db = db

    def create_measurement(self, measurement_data: MeasurementBase):
        try:
            if measurement_data.latitude is None or measurement_data.longitude is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Brak wymaganych współrzędnych"
                )

            timestamp = measurement_data.timestamp or datetime.utcnow()
            
            new_measurement = Measurement(
                latitude=measurement_data.latitude,
                longitude=measurement_data.longitude,
                signal_strength=measurement_data.signal_strength,
                download_speed=measurement_data.download_speed,
                upload_speed=measurement_data.upload_speed,
                ping=measurement_data.ping,
                timestamp=timestamp,
                color=self.calculate_color(measurement_data.download_speed)
            )
            
            self.db.add(new_measurement)
            self.db.commit()
            self.db.refresh(new_measurement)
            return new_measurement
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )


    def get_measurement(self, measurement_id: int):
        measurement = self.db.query(Measurement).get(measurement_id)
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pomiar nie znaleziony"
            )
        return measurement

    def get_measurements(self, skip: int = 0, limit: int = 50):
        MAX_LIMIT = 200
        if limit > MAX_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maksymalny limit pobieranych danych to {MAX_LIMIT}"
            )
        return self.db.query(Measurement).order_by(Measurement.timestamp.desc()).offset(skip).limit(limit).all()

    def get_measurements_nearby(self, latitude, longitude, radius_km: float = 1.0, skip: int = 0, limit: int = 50):
        from sqlalchemy.sql import text

        query = text("""
            SELECT *, 
                   (6371 * acos(
                       cos(radians(:latitude)) * cos(radians(latitude)) * 
                       cos(radians(longitude) - radians(:longitude)) + 
                       sin(radians(:latitude)) * sin(radians(latitude))
                   )) AS distance
            FROM measurement
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            HAVING distance <= :radius_km
            ORDER BY distance
            LIMIT :limit OFFSET :skip
        """)

        result = self.db.execute(query, {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "limit": limit,
            "skip": skip
        }).fetchall()

        return [Measurement(**row) for row in result]

    def update_measurement(self, measurement_id: int, measurement_data: MeasurementUpdate):
        db_measurement = self.get_measurement(measurement_id)
        
        update_data = measurement_data.model_dump(exclude_unset=True)
        
        if "download_speed" in update_data:
            update_data["color"] = self.calculate_color(update_data["download_speed"])
        
        try:
            for key, value in update_data.items():
                setattr(db_measurement, key, value)
            
            self.db.commit()
            self.db.refresh(db_measurement)
            return db_measurement
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    def delete_measurement(self, measurement_id: int):
        measurement = self.get_measurement(measurement_id)
        try:
            self.db.delete(measurement)
            self.db.commit()
            return {"message": "Pomiar usunięty"}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    def calculate_color(self, download_speed: float ) -> str:
        """
        Determine color based on download speed thresholds:
        - Red: < 10 Mbps
        - Green: >= 10 Mbps
        - Gray: No speed data
        """
        if download_speed is None:
            return "gray"
        return "red" if download_speed < 10 else "green"
