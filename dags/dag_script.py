from datetime import timedelta
from airflow import DAG
import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from scripts.extraction import extraction 
from scripts.transformation import transformation
from scripts.loading import loading


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    dag_id="zipco_food_dag",
    default_args=default_args,
    description="Zipco batch ETL pipeline",
    start_date=pendulum.datetime(2026, 8, 16, tz="Europe/Helsinki"),
    schedule="*/10 * * * *",  # Use None for manual execution
    catchup=False,
    tags=["zipco", "etl"],
) as dag:

    extraction_task = PythonOperator(
        task_id="extraction_layer",
        python_callable=extraction,
        do_xcom_push=False,
    )

    transformation_task = PythonOperator(
        task_id="transformation_layer",
        python_callable=transformation,
        do_xcom_push=False,
    )

    loading_task = PythonOperator(
        task_id="loading_layer",
        python_callable=loading,
        do_xcom_push=False,
    )

    extraction_task >> transformation_task >> loading_task
