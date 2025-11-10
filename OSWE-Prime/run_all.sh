#!/bin/bash
set -e
ROOT=$(pwd)
echo "Running Project A setup and tests"
cd Project_A_Baseline_Search
if [ ! -d ".venv" ]; then ./setup.sh; fi
source .venv/bin/activate
./run_tests.sh
deactivate
cd $ROOT

echo "Running Project B setup and tests"
cd Project_B_SearchHistory
if [ ! -d ".venv" ]; then ./setup.sh; fi
source .venv/bin/activate
./run_tests.sh
deactivate
cd $ROOT

mkdir -p results
python - <<'PY'
import json,os
pre = os.path.join('Project_A_Baseline_Search','results','results_pre.json')
post = os.path.join('Project_B_SearchHistory','results','results_post.json')
pre_data = []
post_data = []
if os.path.exists(pre): pre_data = json.load(open(pre))
if os.path.exists(post): post_data = json.load(open(post))
out = {'results_pre': pre_data, 'results_post': post_data}
open('results/aggregated_results.json','w').write(json.dumps(out, indent=2))
print('Aggregated results written to results/aggregated_results.json')
PY

echo "Generating markdown report"
python scripts/generate_report.py


echo "Comparison complete"
