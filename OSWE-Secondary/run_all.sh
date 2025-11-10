#!/usr/bin/env bash
# Master script to run baseline then post-feature tests and create a compare report
set -e
ROOT=$(pwd)

# Setup and run baseline
cd Project_A_Baseline_Search
./setup.sh
pytest -q || true
cd $ROOT

# Setup and run post-feature
cd Project_B_SearchHistory
./setup.sh
pytest -q || true
cd $ROOT

# aggregate
python - <<'PY'
import json, os
root='.'
pre='Project_A_Baseline_Search/results/results_pre.json'
post='Project_B_SearchHistory/results/results_post.json'
res_pre = json.load(open(pre)) if os.path.exists(pre) else []
res_post = json.load(open(post)) if os.path.exists(post) else []
agg = {'pre': res_pre, 'post': res_post}
open('results/aggregated_metrics.json','w').write(json.dumps(agg, indent=2))
print('Wrote aggregated metrics')
PY

# generate compare_report.md
python compare_report.py
