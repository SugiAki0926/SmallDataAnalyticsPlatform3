from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="tag_sync_demo",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dap3", "git-sync", "v2"],
) as dag:
    show_dag_revision = BashOperator(
        task_id="show_dag_revision",
        bash_command="echo 'DAG code from dap3 (v2)'",
    )
