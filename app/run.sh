#!/bin/sh
set -eu
echo "dap3 task code is running"
echo "app version:"
cat /app/git/repo/app/VERSION
dbt --version
dbt run \
  --project-dir /app/git/repo/transform/dap3-dbt \
  --profiles-dir /app/git/repo/transform/dap3-dbt
