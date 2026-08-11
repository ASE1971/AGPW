# AGPW

AGPW to prosty projekt API napisany w FastAPI. Aplikacja udostępnia endpoint zdrowia oraz jest przygotowana do uruchamiania w kontenerze Docker i automatycznego wdrażania przez GitHub Actions.

## Funkcje
- prosty endpoint `/health`
- obsługa Dockera
- workflow CI/CD na GitHub Actions
- testy automatyczne

## Uruchamianie lokalne

### Wymagania
- Python 3.11+
- pip
 - pandas, openpyxl, xlrd (do odczytu plików Excel, instalowane przez `requirements.txt`)

### Instalacja
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Uruchomienie aplikacji
```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

## Uruchamianie z Dockerem
```bash
docker build -f docker/Dockerfile -t agpw .
docker run -p 8000:8000 agpw
```

## Ingest plików Excel (lokalnie)

Pliki Excel wrzucane do katalogu `data/incoming` są przetwarzane przez skrypt ingest który:
- klasyfikuje plik (akcje/indeksy/UNKNOWN),
- mapuje i waliduje kolumny,
- zapisuje dane do SQLite (`data/agpw.db`),
- po sukcesie usuwa plik z folderu `incoming`, a `UNKNOWN` przenosi do `data/incoming/unknown/`.

Uruchomienie:
```bash
python -m agent.ingest.run_ingest -d data/incoming
```

## Testy
```bash
pytest -q
```

Uwaga: testy używają `pandas` i czytają przykładowe pliki Excel — upewnij się, że zainstalowano zależności z `requirements.txt`.

## CI/CD
Projekt korzysta z GitHub Actions:
- uruchamia testy przy każdym pushu i pull requestcie
- buduje obraz Dockera
- publikuje obraz do GitHub Container Registry

Ważne: workflow CI instaluje teraz `pandas`, `openpyxl` i `xlrd` przed uruchomieniem testów (zdefiniowane w `.github/workflows/ci-cd.yml`).

## Struktura projektu
- `api/` — kod aplikacji FastAPI
- `docker/` — pliki Dockera
- `tests/` — testy automatyczne
- `.github/workflows/` — workflowy GitHub Actions

## Rekomendacje dalszego rozwoju
Projekt można rozwinąć w kierunku pełnego systemu analitycznego GPW:

- dodać `data/db.py` i zdefiniować schemat SQLite z tabelami:
  - `stocks_daily`, `indexes_daily`, `tickers`, `sectors`, `sector_companies`, `sector_index_map`
- rozbudować moduł ingest w `agent/ingest/`:
  - klasyfikacja plików Excel przez lokalny LLM
  - walidacja danych i mapowanie kolumn
  - zapis wyników do SQLite
  - logowanie i obsługa błędów
- wdrożyć pipeline multi-agentowy:
  - ingest → validate → analyze → anomalies → scoring → report
- dodać API w `api/routes/`:
  - `/api/chat` — orchestrator
  - `/api/fetch/eod` — pobranie danych
  - `/api/score/{ticker}` — scoring
- wzmocnić CI/CD:
  - lint (ruff), type-check (mypy), testy (pytest), security scan (bandit)
  - build Docker, push do registry, deploy/restart kontenerów
- przygotować komplet testów:
  - ingest, klasyfikator LLM, DB, pipeline, API
- zadbać o bezpieczeństwo importu Excel:
  - typ pliku, rozmiar, brak makr i ukrytych arkuszy
  - walidacja typów i zakresów danych

## Plan działania
- [ ] `data/db.py` + definicja tabel SQLite
- [ ] `agent/ingest/` + parser plików Excel
- [ ] `agent/file_llm_classifier.py` + klasyfikacja LLM
- [ ] `agent/worker.py` + pipeline multi-agentowy
- [ ] `api/routes/` + endpointy `/api/chat`, `/api/fetch/eod`, `/api/score/{ticker}`
- [ ] rozbudowa `docker-compose.yml` o `ollama`, `worker`, `db_volume`
- [ ] `ci.yml` z lint, mypy, pytest, bandit
- [ ] `cd.yml` z push do registry i deployem
- [ ] testy jednostkowe i integracyjne dla ingest/pipeline/API
- [ ] walidacja i zabezpieczenie importu Excel

Te kroki pozwolą przekształcić projekt w system analityczny z pełnym ingestem, oceną i raportowaniem.