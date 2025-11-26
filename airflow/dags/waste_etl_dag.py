from datetime import datetime
import os
import sys

# Make repository code importable from within the container
PROJECT_DIR = "/opt/airflow/ETL-Climate-Insight"
if PROJECT_DIR not in sys.path:
	sys.path.insert(0, PROJECT_DIR)

from airflow import DAG
from airflow.operators.empty import EmptyOperator


with DAG(
	dag_id="waste_etl_dag",
	description="Placeholder DAG for Waste ETL",
	start_date=datetime(2025, 1, 1),
	schedule=None,
	catchup=False,
) as dag:
	start = EmptyOperator(task_id="start")
	done = EmptyOperator(task_id="done")

	start >> done