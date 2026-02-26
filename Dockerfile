FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install local sso_auth wheel
COPY vendor/ vendor/
RUN pip install --no-cache-dir vendor/*.whl

COPY src/ src/
COPY app.py .

# Default: run the ETL flow (overridden by docker-compose for streamlit)
CMD ["python", "-m", "src.etl_flow"]
