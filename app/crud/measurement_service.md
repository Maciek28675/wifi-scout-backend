### `MeasurementService`

Klasa `MeasurementService` zarządza logiką biznesową związaną z pomiarami sieciowymi.

**Metody:**

- **`__init__(self, db: Session)`**
  - Inicjalizuje serwis, ustawiając sesję bazy danych (`db`), próg bliskości dla agregatów (`proximity_threshold_meters`) oraz rozmiar strefy (`zone_size_meters`).
- **`generate_zone_id(self, lat: float, lon: float) -> str`**
  - Generuje unikalny identyfikator strefy na podstawie podanych współrzędnych geograficznych (szerokość, długość) i zdefiniowanego rozmiaru strefy.
- **`generate_geohash(self, lat: float, lon: float, precision: int = 7) -> str`**
  - Generuje geohash dla podanych współrzędnych geograficznych z określoną precyzją.
- **`find_or_create_aggregate(self, lat: float, lon: float, download_speed: Optional[float], upload_speed: Optional[float], ping: Optional[int]) -> int`**
  - Wyszukuje istniejący agregat pomiarów (`MeasurementAggregate`) w bliskiej odległości od podanych współrzędnych.
  - Jeśli odpowiedni agregat istnieje i znajduje się w zdefiniowanym progu bliskości, aktualizuje go o nowe dane pomiarowe.
  - Jeśli nie, tworzy nowy agregat.
  - Zwraca ID znalezionego lub utworzonego agregatu.
- **`_update_aggregate(self, agg: MeasurementAggregate, download_speed: Optional[float], upload_speed: Optional[float], ping: Optional[int])`**
  - Prywatna metoda pomocnicza do aktualizacji istniejącego agregatu (`agg`) nowymi danymi pomiarowymi (prędkość pobierania, wysyłania, ping). Aktualizuje liczbę pomiarów, sumy, średnie, minima, maksima oraz czas ostatniego pomiaru i kolor.
- **`create_measurement(self, measurement_data: MeasurementBase) -> Measurement`**
  - Tworzy nowy wpis pomiaru (`Measurement`) w bazie danych.
  - Wymaga współrzędnych geograficznych.
  - Generuje `zone_id` i `geohash`.
  - Wywołuje `find_or_create_aggregate` w celu znalezienia lub utworzenia odpowiedniego agregatu dla tego pomiaru.
  - Oblicza kolor na podstawie prędkości pobierania.
  - Zapisuje nowy pomiar i zwraca utworzony obiekt.
- **`get_measurement(self, measurement_id: int)`**
  - Pobiera pojedynczy pomiar z bazy danych na podstawie jego `measurement_id`.
  - Zgłasza `HTTPException` (404), jeśli pomiar nie zostanie znaleziony.
- **`get_measurements(self, skip: int = 0, limit: int = 50)`**
  - Pobiera listę pomiarów z bazy danych z możliwością paginacji (`skip`, `limit`).
  - Nakłada maksymalny limit pobieranych danych (domyślnie 200).
  - Sortuje wyniki malejąco według znacznika czasu.
- **`get_measurements_nearby(self, latitude: float, longitude: float, radius_km: float = 1.0, skip: int = 0, limit: int = 50) -> List[dict]`**
  - Wyszukuje agregaty pomiarów (`MeasurementAggregate`) w określonym promieniu (`radius_km`) od podanej lokalizacji (szerokość, długość).
  - Najpierw identyfikuje strefę (`zone_id`) dla podanej lokalizacji.
  - Następnie filtruje agregaty w tej strefie, które mieszczą się w zadanym promieniu.
  - Zwraca listę słowników zawierających dane agregatów oraz obliczoną odległość, posortowaną według odległości.
- **`update_measurement(self, measurement_id: int, measurement_data: MeasurementUpdate)`**
  - Aktualizuje istniejący pomiar w bazie danych na podstawie jego `measurement_id` i dostarczonych danych (`measurement_data`).
  - Jeśli aktualizowana jest prędkość pobierania, przelicza również kolor.
- **`delete_measurement(self, measurement_id: int)`**
  - Usuwa pomiar z bazy danych na podstawie jego `measurement_id`.
- **`calculate_color(self, download_speed: float) -> str`**
  - Oblicza i zwraca reprezentację koloru ("red", "green", "gray") na podstawie wartości prędkości pobierania.
    - "red": prędkość < 10 Mbps
    - "green": prędkość >= 10 Mbps
    - "gray": brak danych o prędkości
- **`update_zone_statistics(self, zone_id: str)`**
  - Aktualizuje statystyki dla określonej strefy pomiarowej (`MeasurementZone`) na podstawie wszystkich pomiarów (`Measurement`) należących do tej strefy.
  - Jeśli strefa nie istnieje, tworzy ją, obliczając jej granice na podstawie współrzędnych pomiarów.
  - Oblicza całkowitą liczbę pomiarów, średnie prędkości pobierania/wysyłania, średni ping oraz daty pierwszego i ostatniego pomiaru w strefie.
