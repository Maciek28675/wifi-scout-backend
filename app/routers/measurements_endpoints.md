### Endpointy API systemu pomiarowego

#### `POST /measurements/` – Tworzenie nowego pomiaru

Implementuje mechanizm dodawania nowych rekordów pomiarowych z automatyczną aktualizacją statystyk strefy w tle. Wymaga pełnych danych geograficznych (latitude, longitude) oraz parametrów sieciowych. W odpowiedzi zwraca obiekt `MeasurementResponse` z walidacją Pydantic.

#### `GET /measurements/{measurement_id}` – Pobieranie pojedynczego pomiaru

Udostępnia szczegółowe dane pomiaru w formacie JSON poprzez ID, z automatycznym mapowaniem modelu ORM na schemat odpowiedzi. Zastosowano optymalne zapytania SQL z wykorzystaniem indeksów głównych.

#### `GET /measurements/` – Lista pomiarów z filtrami

Obsługuje stronicowanie (`skip`, `limit`) i zaawansowane filtrowanie po strefach (`zone_id`) oraz parametrach sieci (`min_speed`). Implementuje walidację parametrów zapytania z użyciem `Query` z ograniczeniami liczbowymi.

#### `PUT /measurements/{measurement_id}` – Aktualizacja pomiaru

Umożliwia modyfikację istniejącego rekordu z równoczesną aktualizacją statystyk zarówno bieżącej jak i poprzedniej strefy. Wykorzystuje transakcyjne operacje bazodanowe z obsługą wyjątków.

#### `DELETE /measurements/{measurement_id}` – Usuwanie pomiaru

Implementuje bezpieczne usuwanie rekordów z kaskadową aktualizacją statystyk strefy i agregatów. Zastosowano mechanizm pobierania pełnego obiektu przed operacją usunięcia.

#### `GET /measurements/nearby` – Wyszukiwanie przestrzenne

Realizuje geograficzne zapytania promieniowe z użyciem algorytmu Haversine. Parametry: `latitude`, `longitude`, `radius_km` z automatyczną konwersją jednostek. Optymalizacja poprzez indeksy złożone na współrzędnych.

#### `GET /measurements/aggregates/` – Agregaty pomiarowe

Udostępnia zagregowane dane statystyczne z możliwością filtrowania po strefach (`zone_id`) i minimalnej liczbie pomiarów (`min_measurements`). Zastosowano precyzyjne obliczenia średnich z użyciem funkcji SQL.

#### `GET /zones/{zone_id}/stats` – Statystyki strefowe

Generuje kompleksowy raport statystyczny dla strefy uwzględniający: granice geograficzne, metryki sieciowe, trendy czasowe. Zawiera szczegółowe dane o rozmieszczeniu agregatów.

#### `POST /distance` – Obliczenia geodezyjne

Implementuje algorytm Haversine do obliczania odległości między współrzędnymi. Zwraca wyniki w metrach i kilometrach z precyzją do 3 miejsc po przecinku.

#### `GET /zones/` – Lista stref pomiarowych

Udostępnia metadane stref z paginacją, zawierające kluczowe wskaźniki efektywności sieci w obrębie strefy. Zoptymalizowano pod kątem szybkiego dostępu poprzez indeksy złożone.
