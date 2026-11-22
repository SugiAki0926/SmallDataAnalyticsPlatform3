import os
from datetime import datetime
from pathlib import Path

import yaml
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.bash import BashOperator

DAGS_DIR = Path(__file__).parent
DAP3_ENV = os.environ.get("DAP3_ENV", "dev")
CONFIG_PATH = DAGS_DIR / "dag_config" / DAP3_ENV / "tag_sync_demo.yml"

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    DAG_CONFIG = yaml.safe_load(f)

POD_TEMPLATE = DAGS_DIR / DAG_CONFIG["pod_template_file"]

with DAG(
    dag_id="tag_sync_demo",
    dag_display_name="タグのDAG Syncデモ",
    description="タグのDAG Syncデモ",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dap3", "git-sync", "v6", DAP3_ENV],
) as dag:
    show_dag_revision = BashOperator(
        task_id="show_dag_revision",
        bash_command=f"echo 'DAG code from dap3 (v6, env={DAP3_ENV})'",
    )

    show_worker = BashOperator(
        task_id="show_worker",
        bash_command="echo task is running; hostname",
    )

    execute_version = KubernetesPodOperator(
        task_id="execute_version",
        namespace=DAG_CONFIG["namespace"],
        pod_template_file=str(POD_TEMPLATE),
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod",
    )

    show_dag_revision >> show_worker >> execute_version
