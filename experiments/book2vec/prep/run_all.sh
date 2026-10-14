#!/usr/bin/env bash
# Run the whole prep, one step at a time, one book at a time. Every step skips work that is
# already done, so this can be re-run after a failure or after adding rows to the testbed.
#
#   prep/run_all.sh                      # testbed.csv, all books
#   prep/run_all.sh testbed.dev.csv      # another testbed
#   prep/run_all.sh testbed.csv key1 key2   # only these keys
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
py="$here/.venv/bin/python"
testbed="${1:-$here/testbed.csv}"
shift || true
only=()
if [ "$#" -gt 0 ]; then only=(--only "$@"); fi

free_gb() { df -g "$here" | awk 'NR==2 {print $4}'; }

for step in fetch clean annotate mask chunk; do
  if [ "$(free_gb)" -lt 2 ]; then
    echo "less than 2 GB of disk free, stopping before $step" >&2
    exit 1
  fi
  echo "== $step ($(free_gb) GB free) =="
  "$py" "$here/prep/$step.py" --testbed "$testbed" ${only[@]+"${only[@]}"}
done
