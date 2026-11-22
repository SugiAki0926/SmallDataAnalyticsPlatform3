from datetime import datetime
from pathlib import Path

impost broken_for_ci_test

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.bash import BashOperator

POD_TEMPLATE = Path(__file__).parent / "pod_templates" / "task-pod.yaml"


with DAG(
    dag_id="tag_sync_demo",
    dag_display_name="タグのDAG Syncデモ",
    description="タグのDAG Syncデモ",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dap3", "git-sync", "v5"],
) as dag:
    show_dag_revision = BashOperator(
        task_id="show_dag_revision",
        bash_command="echo 'DAG code from dap3 (v5)'",
    )

    show_worker = BashOperator(
        task_id="show_worker",
        bash_command="echo task is running; hostname",
    )

    execute_version = KubernetesPodOperator(
        task_id="execute_version",
        namespace="airflow-dev-namespace",
        pod_template_file=str(POD_TEMPLATE),
        in_cluster=True,
        get_logs=True,
        on_finish_action="keep_pod",
    )

    show_dag_revision >> show_worker >> execute_version
