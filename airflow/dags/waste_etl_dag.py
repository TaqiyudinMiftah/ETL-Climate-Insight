from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "adn",
    "start_date": datetime(2024, 1, 1)
}

with DAG(
    "climate_etl",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
):

    run_etl = BashOperator(
        task_id="run_etl_scripts",
        bash_command="python /app/src/main_etl.py",
        cwd="/app"
    )
