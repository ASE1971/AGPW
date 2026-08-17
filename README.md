SKOPIUJ I WKLEJ — GOTOWY README.md
Kod
# AGPW – System Ingestu i API dla danych GPW

AGPW to projekt łączący ingest danych giełdowych z GPW, lokalną analizę, klasyfikację plików Excel oraz lekkie API oparte na FastAPI. System działa lokalnie (offline), wykorzystuje SQLite jako bazę danych, a ingest obsługuje różne typy plików Excel (akcje, indeksy, tickery, sektory). Projekt jest przygotowany do uruchamiania w Dockerze oraz posiada workflow CI/CD w GitHub Actions.

## Funkcje

### API (FastAPI)
- endpoint zdrowia `/health`
- gotowa struktura pod przyszłe endpointy:
  - `/api/chat`
  - `/api/fetch/eod`
  - `/api/score/{ticker}`

### Ingest danych GPW
- klasyfikacja plików Excel (LLM + heurystyki)
- walidacja i mapowanie kolumn
- zapis danych do SQLite (`data/agpw.db`)
- przenoszenie plików UNKNOWN do `data/incoming/unknown/`
- usuwanie plików po imporcie

### CI/CD
- testy automatyczne (pytest)
- budowanie obrazu Dockera
- publikacja obrazu do GitHub Container Registry
- instalacja zależności (pandas, openpyxl, xlrd) przed testami

## Uruchamianie lokalne

### Wymagania
- Python 3.14+
- pip
- zależności z `requirements.txt` (pandas, openpyxl, xlrd, FastAPI, Uvicorn, pytest)

### Instalacja
```bash
python -m venv .venv
source .venv/bin/activate  # lub .venv\Scripts\Activate.ps1 na Windows
pip install -r requirements.txt
```

### Uruchomienie API
```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### Uruchamianie z Dockerem
```bash
docker build -f docker/Dockerfile -t agpw .
docker run -p 8000:8000 agpw
```

### Ingest plików Excel

Pliki wrzucane do `data/incoming/` są automatycznie przetwarzane:

1. Klasyfikacja typu pliku
2. Walidacja danych
3. Zapis do SQLite
4. Przenoszenie plików (UNKNOWN → `data/unknown/`, poprawne → `data/loaded/`)
5. Usuwanie plików po imporcie

**Obsługiwane typy plików:**

| Typ | Wymagane kolumny |
|-----|-----------------|
| STOCK_DAILY | `isin`, `date` (+ Open, High, Low, Close) |
| INDEX_DAILY | `date` (+ Open, High, Low, Close, nazwa) |
| TICKER_MAP | `ticker`, `name` |
| SECTOR_COMPOSITION | `sector`, `ticker` |
| SECTOR_INDEX_MAP | `sector`, `index_name` |

**Uruchomienie ingestu:**
```bash
python -m agent.ingest.run_ingest --dir data/incoming
```

## Testy

Projekt zawiera 6 testów automatycznych pokrywających:
- odczyt plików Excel
- klasyfikację plików
- ingest danych
- obsługę nieznanych plików
- health endpoint API

Uruchomienie testów:
```bash
python -m pytest -v
```

Wynik: ✅ Wszystkie 6 testów przechodzi

## Struktura projektu

```
.
├── api/                      # FastAPI aplikacja
├── agent/ingest/             # Logika ingestu i klasyfikacji
├── data/                     # Baza SQLite + pliki wejściowe
│   ├── agpw.db
│   ├── incoming/
│   ├── loaded/
│   └── unknown/
├── docker/                   # Dockerfile i konfiguracja
├── tests/                    # Testy automatyczne
├── scripts/                  # Skrypty pomocnicze
├── .github/workflows/        # CI/CD
└── requirements.txt          # Zależności Python
```

**Kluczowe moduły:**
- `data/db.py` — schemat i operacje na SQLite
- `agent/ingest/file_router.py` — główny orkestrator ingestu
- `agent/ingest/file_llm_classifier.py` — klasyfikacja plików
- `agent/ingest/ingest_stocks_daily.py` — ingest danych akcji
- `agent/ingest/ingest_indexes_daily.py` — ingest danych indeksów

## Rekomendacje dalszego rozwoju

- ✅ Testy automatyczne (6/6 testów przechodzi)
- ⏳ Rozbudowa LLM — integracja z API do klasyfikacji plików
- ⏳ Walidacja danych — bardziej zaawansowana walidacja Excel
- ⏳ Pipeline multi-agentowy: ingest → validate → analyze → anomalies → scoring → report
- ⏳ Nowe endpointy API: `/api/chat`, `/api/fetch/eod`, `/api/score/{ticker}`
- ⏳ Narzędzia: ruff, mypy, bandit, deployment automation
- ⏳ Obsługa więcej formatów danych (CSV, JSON)
- ⏳ Monitoring i logging

## CI/CD

Projekt wykorzystuje GitHub Actions do:
- Uruchamiania testów na każde push/PR
- Budowania obrazu Dockera
- Publikacji do GitHub Container Registry
- Walidacji kodu (pylint, type checking)

---

**Status:** ✅ Projekt w aktywnym rozwoju. Ostatnia aktualizacja: 2026-08-17