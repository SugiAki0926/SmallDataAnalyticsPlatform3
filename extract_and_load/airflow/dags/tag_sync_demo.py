from datetime import datetime

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="tag_sync_demo",
    dag_display_name="タグのDAG Syncデモ",
    description="タグのDAG Syncデモ",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dap3", "git-sync", "v3"],
) as dag:
    show_dag_revision = BashOperator(
        task_id="show_dag_revision",
        bash_command="echo 'DAG code from dap3 (v3)'",
    )
    show_worker = BashOperator(
        task_id="show_worker",
        bash_command="echo task is running; hostname; sleep 15",
    )
    execute_version = KubernetesPodOperator(
        task_id="execute_version",
        name="execute-version",
        namespace="airflow-dev-namespace",
        image="dap3-task:local",
        image_pull_policy="IfNotPresent",
        cmd=["sh", "-c"],
        arguments=["echo task pod started; hostname; sleep 10"],
        n_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod",
    )

    show_dag_revision >> show_worker >> execute_version
