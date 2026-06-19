#!/bin/bash
set -e

echo "⏳ Waiting for SQL Server to be ready..."

# Wait up to 60 seconds for SQL Server to accept connections
for i in $(seq 1 30); do
    if python -c "
import pyodbc, os
conn_str = os.environ.get('DATABASE_URL', '')
# Extract server from SQLAlchemy URL for a quick connectivity check
try:
    pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=db,1433;'
        'UID=sa;'
        'PWD=${SA_PASSWORD};'
        'Connection Timeout=5;'
    )
    exit(0)
except:
    exit(1)
" 2>/dev/null; then
        echo "✅ SQL Server is ready!"
        break
    fi
    echo "   Attempt $i/30 – SQL Server not ready yet, retrying in 2s..."
    sleep 2
done

# ── Create databases if they don't exist ──
echo "🗄️  Ensuring databases exist..."
python -c "
import pyodbc, os
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=db,1433;'
    'UID=sa;'
    'PWD=${SA_PASSWORD};',
    autocommit=True
)
cursor = conn.cursor()
for db_name in ['CarRentalDB']:
    cursor.execute(f\"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{db_name}') CREATE DATABASE [{db_name}]\")
    print(f'   ✅ Database {db_name} ensured.')
conn.close()
"

# ── Run Flask migrations ──
echo "🔄 Running Flask database migrations..."
flask db upgrade || echo "⚠️  Migrations skipped (may need 'flask db init' first)"

# ── Start Gunicorn ──
echo "🚀 Starting Gunicorn on port 5000..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 manage:app
