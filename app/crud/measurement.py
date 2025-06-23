from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func
from app.models import Measurement
from app.schemas import MeasurementBase, MeasurementUpdate, MeasurementResponse
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Union
from app.utils.distance_utils import (
    haversine_distance,
)
from app.utils.buildings import find_building


class MeasurementService:
    def __init__(self, db: Session):
        self.db = db
        self.proximity_threshold_meters = 4.0

    def create_measurement(self, measurement_data: MeasurementBase) -> Measurement:
        """Stwórz nowy pomiar i przypisz do odpowiedniej strefy"""
        try:
            if measurement_data.latitude is None or measurement_data.longitude is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Brak wymaganych współrzędnych",
                )

            utc_plus_2 = timezone(timedelta(hours=2))
            timestamp = datetime.now(utc_plus_2)

            new_measurement = Measurement(
                latitude=measurement_data.latitude,
                longitude=measurement_data.longitude,
                height=measurement_data.height,
                download_speed=measurement_data.download_speed,
                upload_speed=measurement_data.upload_speed,
                ping=measurement_data.ping,
                building_name=find_building(
                    measurement_data.latitude,
                    measurement_data.longitude ),
                timestamp=timestamp,
                color=self.calculate_color(
                    measurement_data.download_speed, 
                    measurement_data.upload_speed,
                    measurement_data.ping ),
                measurement_count=1,
                download_speed_sum=measurement_data.download_speed,
                upload_speed_sum=measurement_data.upload_speed,
                ping_sum=measurement_data.ping
            )

            # Get measurements in the same building
            measurements_in_bulidng = ( 
                self.db.query(Measurement)
                .filter(Measurement.building_name == new_measurement.building_name)
                .order_by(Measurement.timestamp.desc())
                .all() 
            )

            updated_or_created_measurement = None

            for measurement in measurements_in_bulidng:
                d = haversine_distance( 
                    new_measurement.latitude,
                    new_measurement.longitude, 
                    measurement.latitude, 
                    measurement.longitude   
                )

                # if new measurement is within 5 meters of exisitng measurement and on the same alt then update
                if d <= 5 and (measurement.height-1 <= measurement.height <= measurement.height+1):
                    update_measurement_data = MeasurementUpdate(
                        latitude=new_measurement.latitude,
                        longitude=new_measurement.longitude,
                        height=new_measurement.height,
                        download_speed=new_measurement.download_speed,
                        upload_speed=new_measurement.upload_speed,
                        ping=new_measurement.ping,
                        timestamp=timestamp,
                        building_name=new_measurement.building_name 
                    )
                    updated_or_created_measurement = self.update_measurement(measurement.id, update_measurement_data)
                    print(f'Measurement ID: {measurement.id} updated.')
                    break
            
            if not updated_or_created_measurement:
                self.db.add(new_measurement)
                self.db.commit()
                self.db.refresh(new_measurement)
                updated_or_created_measurement = new_measurement
                print(f'Nearby measurement not found. New measurement added.')
            
            return updated_or_created_measurement

        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error podczas tworzenia pomiaru: {str(e)}",
            )

    def get_measurement(self, measurement_id: int):
        measurement = self.db.get(Measurement, measurement_id)
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pomiar nie znaleziony"
            )
        return measurement

    def get_measurements(
        self,
        skip: int = 0,
        limit: int = 50,
        building_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 1.0,
    ) -> Union[List[MeasurementResponse], List[dict]]:
        """
        Jeśli podano building_name – zwróć pomiary dla tego budynku.
        Jeśli podano latitude i longitude – zwróć agregaty w promieniu radius_km.
        """
        MAX_LIMIT = 200
        if limit > MAX_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maksymalny limit to {MAX_LIMIT}"
            )

        if building_name:
            return (
                self.db.query(Measurement)
                .filter(Measurement.building_name == building_name)
                .order_by(Measurement.timestamp.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

        if latitude is not None and longitude is not None:
            radius_m = radius_km * 1000
            delta = radius_km * 0.01
            records = self.db.query(Measurement).filter(
                Measurement.latitude.between(latitude - delta, latitude + delta),
                Measurement.longitude.between(longitude - delta, longitude + delta)
            ).all()

            results: List[dict] = []
            for m in records:
                d = haversine_distance(latitude, longitude, m.latitude, m.longitude)
                if d <= radius_m:
                    results.append({
                        "id": m.id,
                        "latitude": m.latitude,
                        "longitude": m.longitude,
                        "building_name": m.building_name,
                        # sumy
                        "download_speed_sum": m.download_speed_sum,
                        "upload_speed_sum": m.upload_speed_sum,
                        "ping_sum": m.ping_sum,
                        "measurement_count": m.measurement_count,
                        # średnie
                        "download_speed": m.download_speed,
                        "upload_speed": m.upload_speed,
                        "ping": m.ping,
                        "color": m.color,
                        "timestamp": m.timestamp,
                        # dodatkowo
                        "distance_m": d,
                    })
            results.sort(key=lambda x: x["distance_m"])
            return results[skip: skip + limit]

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Podaj albo building_name, albo latitude i longitude"
        )

    def update_measurement(self, measurement_id: int, new_data: MeasurementUpdate):
        """Add a new measurement to an existing geographic point"""
        db_measurement = self.get_measurement(measurement_id)
        update_data = new_data.model_dump(exclude_unset=True)

        if "timestamp" in update_data:
            db_measurement.timestamp = update_data["timestamp"]

        # 1. Update the sum fields and count
        new_dl = update_data.get("download_speed", 0.0) or 0.0
        new_ul = update_data.get("upload_speed", 0.0) or 0.0
        new_ping = update_data.get("ping", 0) or 0

        db_measurement.download_speed_sum += new_dl
        db_measurement.upload_speed_sum += new_ul
        db_measurement.ping_sum += new_ping
        db_measurement.measurement_count += 1

        # 2. Recalculate averages
        count = db_measurement.measurement_count
        db_measurement.download_speed = db_measurement.download_speed_sum / count
        db_measurement.upload_speed = db_measurement.upload_speed_sum / count
        db_measurement.ping = int(db_measurement.ping_sum / count)

        # 3. Update color if relevant
        db_measurement.color = self.calculate_color(
            db_measurement.download_speed,
            db_measurement.upload_speed,
            db_measurement.ping,
        )

        # 4. Commit updates
        try:
            self.db.commit()
            self.db.refresh(db_measurement)
            return db_measurement

        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error while adding measurement to point: {str(e)}",
            )


    def delete_measurement(self, measurement_id: int):
        """Usuń pojedynczy pomiar z agregatu lub cały agregat jeśli to jedyny pomiar"""
        measurement = self.get_measurement(measurement_id)

        # jeśli jest więcej niż 1 pomiar w agregacie
        if measurement.measurement_count > 1:
            measurement.measurement_count -= 1

            dl = measurement.download_speed or 0.0
            ul = measurement.upload_speed or 0.0
            pg = measurement.ping or 0

            measurement.download_speed_sum -= dl
            measurement.upload_speed_sum -= ul
            measurement.ping_sum -= pg

            # przeliczamy nowe średnie
            measurement.download_speed = measurement.download_speed_sum / measurement.measurement_count
            measurement.upload_speed = measurement.upload_speed_sum / measurement.measurement_count
            measurement.ping = int(measurement.ping_sum / measurement.measurement_count)

            self.db.commit()
            self.db.refresh(measurement)
            return measurement

        try:
            self.db.delete(measurement)
            self.db.commit()
            return {"message": "Pomiar usunięty"}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error podczas usuwania pomiaru: {str(e)}",
            )

    def calculate_color(self, download_speed: float, upload_speed: float, ping: float) -> str:
        """
        Wyznacz kolor na podstawie znormalizowanych i uśrednionych prędkości wyników testu
        """
        
        min_download = 1
        max_download = 200
        min_upload = 1
        max_upload = 100
        min_ping = 8
        max_ping = 600

        normalized_download = ((download_speed - min_download) / (max_download - min_download)) * 100
        normalized_upload = ((upload_speed - min_upload) / (max_upload - min_upload)) * 100
        normalized_ping = (1 - ((ping - min_ping) / (max_ping - min_ping))) * 100

        download_w = 5
        upload_w = 3
        ping_w = 2

        score = (
            (download_w * normalized_download) + 
            (upload_w * normalized_upload) +
            (ping_w * normalized_ping)) / (download_w + upload_w + ping_w)
        
        if score <= 30:
            return '#B22D2D'
        elif score > 30 and score <= 70:
            return '#E4A316'
        elif score > 70:
            return '#67B22D'
        