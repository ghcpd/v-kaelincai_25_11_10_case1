#!/bin/bash
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)

echo "Running Project A (Baseline) tests..."
bash "$ROOT/Project_A_Baseline_Search/run_tests.sh"
cp "$ROOT/Project_A_Baseline_Search/results/results_pre.json" "$ROOT/results/results_pre.json" || true

echo "Running Project B (Search History) tests..."
bash "$ROOT/Project_B_SearchHistory/run_tests.sh"
cp "$ROOT/Project_B_SearchHistory/results/results_post.json" "$ROOT/results/results_post.json" || true

python - <<PY
import json,sys
R='''
Compare Report
==============

'''
try:
    pre=json.load(open('results/results_pre.json'))
except:
    pre={}
try:
    post=json.load(open('results/results_post.json'))
except:
    post={}
agg={'pre':pre,'post':post}
open('results/aggregated_metrics.json','w').write(json.dumps(agg,indent=2))
open('compare_report.md','w').write('# Compare Report\n\nPre and Post results saved to results/aggregated_metrics.json\n')
PY

echo "Done. Artifacts in results/"
