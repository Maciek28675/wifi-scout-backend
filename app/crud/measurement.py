from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func
from app.models import Measurement, MeasurementZone, MeasurementAggregate
from app.schemas import MeasurementBase, MeasurementUpdate
from datetime import datetime
from typing import List, Optional
from app.utils.distance_utils import (
    haversine_distance,
    generate_simple_zone_id,
    generate_simple_geohash,
    find_points_within_radius,
)


class MeasurementService:
    def __init__(self, db: Session):
        self.db = db
        self.proximity_threshold_meters = 4.0
        self.zone_size_meters = 100.0

    def generate_zone_id(self, lat: float, lon: float) -> str:
        """Wygeneruj unikalny identyfikator strefy na podstawie współrzędnych"""
        return generate_simple_zone_id(lat, lon, self.zone_size_meters)

    def generate_geohash(self, lat: float, lon: float, precision: int = 7) -> str:
        """Wygeneruj geohash dla współrzędnych"""
        return generate_simple_geohash(lat, lon, precision)

    def find_or_create_aggregate(
        self,
        lat: float,
        lon: float,
        download_speed: Optional[float],
        upload_speed: Optional[float],
        ping: Optional[int],
    ) -> int:
        """Znajdź lub utwórz agregat dla pomiaru"""
        try:
            zone_id = self.generate_zone_id(lat, lon)

            # Znajdź istniejące agregaty w tej strefie
            existing_aggregates = (
                self.db.query(MeasurementAggregate)
                .filter(MeasurementAggregate.zone_id == zone_id)
                .all()
            )

            # Sprawdź istniejące agregaty w pobliżu
            for agg in existing_aggregates:
                distance = haversine_distance(
                    lat, lon, agg.center_latitude, agg.center_longitude
                )
                if distance <= self.proximity_threshold_meters:
                    # Aktualizacja istniejącego agregatu
                    self._update_aggregate(agg, download_speed, upload_speed, ping)
                    return agg.id

            # Tworzenie nowego agregatu, jeśli nie znaleziono odpowiedniego
            new_agg = MeasurementAggregate(
                zone_id=zone_id,
                center_latitude=lat,
                center_longitude=lon,
                measurement_count=1,
                download_speed_sum=download_speed or 0,
                download_speed_avg=download_speed,
                download_speed_min=download_speed,
                download_speed_max=download_speed,
                upload_speed_sum=upload_speed or 0,
                upload_speed_avg=upload_speed,
                upload_speed_min=upload_speed,
                upload_speed_max=upload_speed,
                ping_sum=ping or 0,
                ping_avg=ping,
                ping_min=ping,
                ping_max=ping,
                first_measurement=datetime.utcnow(),
                last_measurement=datetime.utcnow(),
                color=self.calculate_color(download_speed),
            )

            self.db.add(new_agg)
            self.db.flush()
            return new_agg.id

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error podczas tworzenia agregatu: {str(e)}",
            )

    def _update_aggregate(
        self,
        agg: MeasurementAggregate,
        download_speed: Optional[float],
        upload_speed: Optional[float],
        ping: Optional[int],
    ):
        """Update aggregate with new measurement data"""
        agg.measurement_count += 1

        if download_speed is not None:
            agg.download_speed_sum = (agg.download_speed_sum or 0) + download_speed
            agg.download_speed_avg = agg.download_speed_sum / agg.measurement_count
            agg.download_speed_min = min(
                agg.download_speed_min or float("inf"), download_speed
            )
            agg.download_speed_max = max(agg.download_speed_max or 0, download_speed)

        if upload_speed is not None:
            agg.upload_speed_sum = (agg.upload_speed_sum or 0) + upload_speed
            agg.upload_speed_avg = agg.upload_speed_sum / agg.measurement_count
            agg.upload_speed_min = min(
                agg.upload_speed_min or float("inf"), upload_speed
            )
            agg.upload_speed_max = max(agg.upload_speed_max or 0, upload_speed)

        if ping is not None:
            agg.ping_sum = (agg.ping_sum or 0) + ping
            agg.ping_avg = agg.ping_sum / agg.measurement_count
            agg.ping_min = min(agg.ping_min or float("inf"), ping)
            agg.ping_max = max(agg.ping_max or 0, ping)

        agg.last_measurement = datetime.utcnow()
        agg.color = self.calculate_color(agg.download_speed_avg)

    def create_measurement(self, measurement_data: MeasurementBase) -> Measurement:
        """Stwórz nowy pomiar i przypisz do odpowiedniej strefy"""
        try:
            if measurement_data.latitude is None or measurement_data.longitude is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Brak wymaganych współrzędnych",
                )

            # Generuj unikalny identyfikator strefy i geohash
            zone_id = self.generate_zone_id(
                measurement_data.latitude, measurement_data.longitude
            )
            geohash = self.generate_geohash(
                measurement_data.latitude, measurement_data.longitude
            )

            # Aggregacja pomiaru
            aggregate_id = self.find_or_create_aggregate(
                measurement_data.latitude,
                measurement_data.longitude,
                measurement_data.download_speed,
                measurement_data.upload_speed,
                measurement_data.ping,
            )

            timestamp = measurement_data.timestamp or datetime.utcnow()

            new_measurement = Measurement(
                latitude=measurement_data.latitude,
                longitude=measurement_data.longitude,
                height=measurement_data.height,
                download_speed=measurement_data.download_speed,
                upload_speed=measurement_data.upload_speed,
                ping=measurement_data.ping,
                timestamp=timestamp,
                color=self.calculate_color(measurement_data.download_speed),
                zone_id=zone_id,
                geohash=geohash,
                aggregate_id=aggregate_id,
            )

            self.db.add(new_measurement)
            self.db.commit()
            self.db.refresh(new_measurement)
            return new_measurement

        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error podczas tworzenia pomiaru: {str(e)}",
            )

    def get_measurement(self, measurement_id: int):
        measurement = self.db.query(Measurement).get(measurement_id)
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pomiar nie znaleziony"
            )
        return measurement

    def get_measurements(self, skip: int = 0, limit: int = 50):
        MAX_LIMIT = 200
        if limit > MAX_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maksymalny limit pobieranych danych to {MAX_LIMIT}",
            )
        return (
            self.db.query(Measurement)
            .order_by(Measurement.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_measurements_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        skip: int = 0,
        limit: int = 50,
    ) -> List[dict]:
        """Wyszukaj pomiary w pobliżu określonej lokalizacji"""
        try:
            radius_meters = radius_km * 1000  # Konwersja km na metry

            # Generuj identyfikator strefy na podstawie współrzędnych
            search_zone_id = self.generate_zone_id(latitude, longitude)

            # Pobierz agregaty w tej strefie
            nearby_aggregates = (
                self.db.query(MeasurementAggregate)
                .filter(MeasurementAggregate.zone_id == search_zone_id)
                .all()
            )

            # Oblicz odległość i filtruj agregaty w promieniu
            results = []
            for agg in nearby_aggregates:
                distance = haversine_distance(
                    latitude, longitude, agg.center_latitude, agg.center_longitude
                )

                if distance <= radius_meters:
                    results.append(
                        {
                            "id": agg.id,
                            "zone_id": agg.zone_id,
                            "center_latitude": agg.center_latitude,
                            "center_longitude": agg.center_longitude,
                            "measurement_count": agg.measurement_count,
                            "download_speed_avg": agg.download_speed_avg,
                            "upload_speed_avg": agg.upload_speed_avg,
                            "ping_avg": agg.ping_avg,
                            "distance_meters": distance,
                            "color": agg.color,
                        }
                    )

            results.sort(key=lambda x: x["distance_meters"])
            return results[skip : skip + limit]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error podczas pobierania pomiarów w pobliżu: {str(e)}",
            )

    def update_measurement(
        self, measurement_id: int, measurement_data: MeasurementUpdate
    ):
        """Aktualizuj istniejący pomiar"""
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
                detail=f"Error podczas aktualizacji pomiaru: {str(e)}",
            )

    def delete_measurement(self, measurement_id: int):
        """Usuń pomiar na podstawie jego ID"""
        measurement = self.get_measurement(measurement_id)
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

    def calculate_color(self, download_speed: float) -> str:
        """
        Wyznacz kolor na podstawie prędkości pobierania:
        - Red: < 10 Mbps
        - Green: >= 10 Mbps
        - Gray: No speed data
        """
        if download_speed is None:
            return "gray"
        return "red" if download_speed < 10 else "green"

    def update_zone_statistics(self, zone_id: str):
        """Update zone statistics based on measurements"""
        try:
            measurements = (
                self.db.query(Measurement).filter(Measurement.zone_id == zone_id).all()
            )

            if not measurements:
                return

            # Znajdź lub utwórz strefę
            zone = (
                self.db.query(MeasurementZone)
                .filter(MeasurementZone.zone_id == zone_id)
                .first()
            )

            if not zone:
                # Oblicz granice strefy na podstawie pomiarów
                lats = [m.latitude for m in measurements]
                lons = [m.longitude for m in measurements]

                zone = MeasurementZone(
                    zone_id=zone_id,
                    min_latitude=min(lats),
                    max_latitude=max(lats),
                    min_longitude=min(lons),
                    max_longitude=max(lons),
                )
                self.db.add(zone)

            zone.total_measurements = len(measurements)

            # Oblicz średnie prędkości i ping
            download_speeds = [
                m.download_speed for m in measurements if m.download_speed
            ]
            upload_speeds = [m.upload_speed for m in measurements if m.upload_speed]
            pings = [m.ping for m in measurements if m.ping]

            if download_speeds:
                zone.zone_avg_download = sum(download_speeds) / len(download_speeds)
            if upload_speeds:
                zone.zone_avg_upload = sum(upload_speeds) / len(upload_speeds)
            if pings:
                zone.zone_avg_ping = sum(pings) / len(pings)

            timestamps = [m.timestamp for m in measurements]
            zone.first_measurement = min(timestamps)
            zone.last_measurement = max(timestamps)

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating zone statistics: {str(e)}",
            )
