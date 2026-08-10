FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# kopiujemy folder api z AGPW
COPY ../api ./api

# kopiujemy requirements z AGPW
COPY ../requirements.txt .

RUN pip install --upgrade pip

# instalujemy uvicorn NORMALNIE
RUN pip install uvicorn fastapi uv

RUN uv pip install -r requirements.txt || true

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
