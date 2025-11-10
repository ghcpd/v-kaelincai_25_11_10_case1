import json, os
PRE='Project_A_Baseline_Search/results/results_pre.json'
POST='Project_B_SearchHistory/results/results_post.json'
pr = json.load(open(PRE)) if os.path.exists(PRE) else []
po = json.load(open(POST)) if os.path.exists(POST) else []
report = []
report.append('# Compare Report')
report.append('\n## Summary')
report.append(f'Pre tests: {len(pr)}, Post tests: {len(po)}')

# basic metrics
pre_pass = sum(1 for r in pr if r.get('expected') == r.get('actual'))
post_pass = sum(1 for r in po if r.get('pass'))
report.append(f'\n- Pre pass count: {pre_pass}\n- Post pass count: {post_pass}\n')

# per-test details
report.append('\n## Per-test details\n')
for r in po:
    report.append(f"- {r.get('id')}: pass={r.get('pass')} notes={r.get('notes', [])} latency={r.get('latency')}")

# metrics
keyboard = [r for r in po if r.get('id') == 'keyboard_navigation']
keyboard_success = sum(1 for r in keyboard if r.get('pass')) / (len(keyboard) or 1)
persist_cases = [r for r in po if 'persistence' in (r or {}) or r.get('id') in ('persistence_and_opt_out','opt_out_disables_persistence')]
persist_success = sum(1 for r in persist_cases if r.get('persistence')) / (len(persist_cases) or 1)
latencies = [r.get('latency') for r in po if r.get('latency') is not None]
avg_latency = sum(latencies)/len(latencies) if len(latencies) else None
report.append(f"\n## Metrics\n- keyboard_navigation_success: {keyboard_success}\n- persistence_success_rate: {persist_success}\n- avg_time_to_dropdown: {avg_latency}\n")

open('compare_report.md','w', encoding='utf-8').write('\n'.join(report))
print('compare_report.md written')
