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
- Python 3.11+
- pip
- zależności z `requirements.txt` (pandas, openpyxl, xlrd, FastAPI, Uvicorn)

### Instalacja
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Uruchomienie API
bash
uvicorn api.server:app --host 0.0.0.0 --port 8000
Uruchamianie z Dockerem
bash
docker build -f docker/Dockerfile -t agpw .
docker run -p 8000:8000 agpw
Ingest plików Excel
Pliki wrzucane do data/incoming/ są automatycznie przetwarzane:

klasyfikacja typu pliku

walidacja danych

zapis do SQLite

przenoszenie plików UNKNOWN

usuwanie plików po imporcie

Uruchomienie ingestu:

bash
python -m agent.ingest.run_ingest -d data/incoming
Testy
bash
pytest -q
Struktura projektu
api/ — aplikacja FastAPI

agent/ingest/ — logika ingestu i klasyfikacji

data/ — baza SQLite + pliki wejściowe

docker/ — Dockerfile i konfiguracja

tests/ — testy automatyczne

.github/workflows/ — CI/CD

Rekomendacje dalszego rozwoju
data/db.py – definicja tabel SQLite

rozbudowa ingest (LLM, walidacja, logowanie)

pipeline multi-agentowy (ingest → validate → analyze → anomalies → scoring → report)

nowe endpointy API (/api/chat, /api/fetch/eod, /api/score/{ticker})

rozbudowa CI/CD (ruff, mypy, bandit, deploy)

testy jednostkowe i integracyjne

walidacja bezpieczeństwa importu Excel

Plan działania
[ ] data/db.py – schemat SQLite

[ ] parser Excel w agent/ingest/

[ ] klasyfikator LLM (file_llm_classifier.py)

[ ] pipeline (agent/worker.py)

[ ] endpointy API

[ ] docker-compose z ollama + worker + db_volume

[ ] CI (lint, mypy, pytest, bandit)

[ ] CD (push do registry + deploy)

[ ] testy ingest/pipeline/API

[ ] walidacja importu Excel

Repozytorium zostało oczyszczone po rewrite historii (13.08.2026). Pliki wykonywalne (*.exe) są ignorowane w .gitignore.