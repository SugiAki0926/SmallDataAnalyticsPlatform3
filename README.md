# SmallDataAnalyticsPlatform3

Kubernetes 上の Apache Airflow が、Git リポジトリの**Gitタグ**を [git-sync](https://github.com/kubernetes/git-sync) で同期する小さな小さなデータ分析基盤です。作って壊すデータ基盤の第3弾で、前回同様、最小構成のためネットワーク、セキュリティ、運用2必要な要素は含まれません。

## git-syncの使用方法について

[git-sync](https://github.com/kubernetes/git-sync) に記載されている通りではあるが、Gitリポジトリをローカルディレクトリにプルし、しばらく待機してから、この処理を繰り返すシンプルなコマンド。リモートリポジトリに変更があると、その変更はローカルにも同期できる。Kubernetesにおける理想的な「サイドカー」コンテナであり、リポジトリからファイルをダウンロードして、アプリケーションがそれらを利用できるようにしてくれます。

このリポジトリでは、同じGitタグを次の2つの git-sync が参照します。Gitタグ `airflow-dag-dev-tag` と `airflow-dag-prod-tag` が、開発 Airflow と本番 Airflow の取り込むコミットを分けます。これにより検証が本番に影響せず、開発を効率よく実行できます。また、GitHub Actions が Gitタグを対象コミットへ付け替えて自動で管理します。

1. **Airflow が DAG を読む git-sync**
   Helm values の `dags.gitSync.ref` にGitタグ名を書いています。Airflow Helm chart はこの値を受け取り、git-sync コンテナでリポジトリを DAG 用ディレクトリに載せます（[Manage DAG files](https://airflow.apache.org/docs/helm-chart/stable/manage-dag-files.html)、[Parameters reference の `dags.gitSync.ref`](https://airflow.apache.org/docs/helm-chart/stable/parameters-ref.html)）。`subPath` は `extract_and_load/airflow/dags` です。
   Executor は KubernetesExecutor です。各タスクはクラスター上のワーカー Pod で動きます（[Kubernetes Executor](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/kubernetes_executor.html)）。永続ボリュームを使わない Git-Sync では、このワーカー Pod の init container としても git-sync が DAG を取得します。

2. **実行用 Pod がコードを取る git-sync**
   DAG の `KubernetesPodOperator` が、別の Pod を起動します（[KubernetesPodOperator](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html)）。その Pod テンプレートでは、公式イメージ `registry.k8s.io/git-sync/git-sync:v4.3.0` を [init container](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) にし、`GITSYNC_REF` に同じGitタグ、`GITSYNC_ONE_TIME=true` を渡しています。`emptyDir` を共有し、メインコンテナは `/app/git/repo` の `app/run.sh` を実行します。init container はアプリより先に完了します。

DAG をパースする git-sync と、実行用 Pod の git-sync は別のコンテナです。どちらもGitタグ名を見ているため、Gitタグが進んだあとに起動した実行用 Pod は、DAG を読んだときとは別のコミットを取ることがあります。起動済みの Pod は、そのボリュームに取得したコミットのまま動きます。
