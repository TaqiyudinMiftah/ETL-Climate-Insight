# Jakarta Climate Data Pipeline

This project is an end-to-end **Data Engineering pipeline** that performs ETL (Extract–Transform–Load) on rainfall and weather data from Jakarta, followed by automated data aggregation and an interactive dashboard built using Streamlit.

## 📌 Project Overview

This repository contains:

* **ETL Pipeline** (`etl_pipeline.py`)
  Extracts raw data, performs cleaning, transformation, and loads the processed data into SQLite.

* **Database Manager** (`db_manager.py`)
  Helper module for database operations such as creating tables, inserting data, and managing connections.

* **Aggregation Script** (`agregasi.py`)
  Processes the cleaned dataset into monthly/yearly trends and exports aggregated views.

* **Streamlit Dashboard** (`app_dashboard.py`)
  Interactive visualization for rainfall trends in Jakarta using the processed data.

* **SQLite Setup** (`setup_sqlite.py`)
  Script to initialize database schema and load initial dataset.

## 📁 Project Structure

```
ETL/
│── agregasi.py
│── app_dashboard.py
│── db_manager.py
│── etl_pipeline.py
│── setup_sqlite.py
│── requirements.txt
│── raw_data/
│── v_jakarta_trend_bulanan.csv
│── v_jakarta_trend_bulanan.sqlite
│── __pycache__/
│── .git/
```

## ⚙️ Installation

Clone the repository and install dependencies:

```bash
git clone <your-repository>
cd ETL
pip install -r requirements.txt
```

## ▶️ Usage

### 1. Setup Database

```bash
python setup_sqlite.py
```

### 2. Run ETL Pipeline

```bash
python etl_pipeline.py
```

### 3. Run Aggregation

```bash
python agregasi.py
```

### 4. Run Dashboard

```bash
streamlit run app_dashboard.py
```

## 🧰 Requirements

* Python 3.9+
* SQLite database
* Streamlit for dashboard
* Pandas for data transformation

## 📊 Dashboard Preview

The Streamlit dashboard allows users to:

* Visualize rainfall trends over months and years
* Analyze aggregated metrics from the cleaned dataset
* Interactively explore weather insights

