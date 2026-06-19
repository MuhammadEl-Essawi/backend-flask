# ──────────────────────────────────────────────
# 🐍 Rently Flask API – Production Dockerfile
# ──────────────────────────────────────────────

FROM python:3.12-slim

# ── System dependencies for pyodbc + ODBC Driver 17 ──
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && apt-get purge -y --auto-remove gcc g++ gnupg2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Install Python dependencies (cached layer) ──
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ──
COPY . /app/

# ── Copy entrypoint script ──
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ── Environment variables ──
ENV FLASK_ENV=production \
    FLASK_APP=manage.py

EXPOSE 5000

# ── Entrypoint: wait for DB → run migrations → start Gunicorn ──
ENTRYPOINT ["/app/entrypoint.sh"]
