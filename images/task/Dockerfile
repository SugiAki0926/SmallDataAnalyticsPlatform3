FROM python:3.12-slim
ARG DBT_DUCKDB_VERSION
RUN python -m pip install --no-cache-dir "dbt-duckdb==${DBT_DUCKDB_VERSION}"
WORKDIR /app
