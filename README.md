# Mini Data Platform

## Overview

This project is an end-to-end data platform built to process and analyze sales data using modern data engineering tools. It generates synthetic sales data, stores raw files in MinIO, processes them with Apache Airflow, loads transformed data into PostgreSQL, and visualizes KPIs in Metabase.

## Prerequisites

* Docker and Docker Compose
* Python 3.12+

## Architecture

```text
+-------------------+
| Data Generation   |
| Python Script     |
+---------+---------+
          |
          v
+-------------------+
| MinIO             |
| Raw CSV Storage   |
+---------+---------+
          |
          v
+-------------------+
| Apache Airflow    |
| ETL Pipeline      |
+---------+---------+
          |
          v
+-------------------+
| PostgreSQL        |
| Data Warehouse    |
+---------+---------+
          |
          v
+-------------------+
| Metabase          |
| KPI Dashboard     |
+-------------------+
```

## Tech Stack

* Python 
* Apache Airflow 
* MinIO 
* PostgreSQL 

## ETL Pipeline

DAG:

```text
sales_etl_pipeline
```

Pipeline flow:

```text
check_source → extract → transform → validate → load
```

## Incremental Loading

The pipeline checks the latest `order_date` in PostgreSQL and loads only new records. This prevents duplicate loading and improves pipeline efficiency.

## Dashboard

### Metabase Sales Dashboard

KPIs included:

* Total Sales
* Average Order Value
* Sales by Product
* Sales by Region
* Daily Sales Trend

![Metabase Dashboard](screenshots/metabase_dashboard.png)

## Project Structure

```text
mini-data-platform/
├── airflow-config/
├── dags/
├── data/
├── scripts/
├── sql/
├── src/
├── tests/
├── screenshots/
├── .github/workflows/
├── .env
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Run the Project

### Environment Variables

A `.env` file is required at the project root. 

```env
# PostgreSQL
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# MinIO
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=

# Airflow
AIRFLOW_ADMIN_USER=
AIRFLOW_ADMIN_PASSWORD=
AIRFLOW_SECRET_KEY=
AIRFLOW_JWT_SECRET=

# Metabase
METABASE_EMAIL=
METABASE_PASSWORD=
```

### Setup

```bash
python3 -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
docker compose up -d
```

### Generate and Upload Data

The MinIO bucket is created automatically by the `minio-init` Docker service on startup. Only the data upload is needed:

```bash
python3 scripts/generate_sample_data.py
python3 scripts/upload_data.py
```

### Run Pipeline

I Open Airflow at `http://localhost:8088` and login with the credentials set in your `.env` (`AIRFLOW_ADMIN_USER` / `AIRFLOW_ADMIN_PASSWORD`).

Trigger DAG:

```text
sales_etl_pipeline
```

### Setup Metabase Dashboard

Once the pipeline has loaded data into PostgreSQL, I run:

```bash
python3 scripts/setup_metabase_dashboard.py
```

### Service Access

| Service       | URL                   |
| ------------- | --------------------- |
| Airflow       | http://localhost:8088 |
| MinIO Console | http://localhost:9001 |
| Metabase      | http://localhost:3001 |

### Run Tests

```bash
pytest tests/
```

## Key Learnings

* ETL pipeline orchestration with Apache Airflow
* Raw data storage with MinIO
* Data cleaning and validation with Python
* Loading transformed data into PostgreSQL
* KPI dashboard development with Metabase
* Deploying services with Docker Compose
* CI/CD automation for data pipelines with GitHub Actions

## Conclusion

This project demonstrates an end-to-end data pipeline from data ingestion to analytics reporting using modern data engineering tools.
