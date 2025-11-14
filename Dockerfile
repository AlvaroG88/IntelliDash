
FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=poll

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      python3-dev \
      build-essential \
      curl \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install -r /app/requirements.txt

COPY . /app

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
