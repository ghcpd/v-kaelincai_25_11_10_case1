import os, json
agg = 'results/aggregated_results.json'
out_md = 'compare_report.md'
if not os.path.exists(agg):
    print('No aggregated results found at', agg); exit(1)
data = json.load(open(agg))
pre = data.get('results_pre', [])
post = data.get('results_post', [])
def compute_metrics(entries):
    total = len(entries)
    correct = sum(1 for e in entries if e.get('pass'))
    keyboard = sum(1 for e in entries if e.get('id','').startswith('keyboard') and e.get('pass'))
    persistence = sum(1 for e in entries if e.get('id','').startswith('persistence') and e.get('pass'))
    latency_list = [e.get('latency') for e in entries if e.get('latency')]
    latency = sum(latency_list)/len(latency_list) if latency_list else None
    return {
        'total': total,
        'correctness_rate': correct/total if total else None,
        'keyboard_success_rate': keyboard/total if total else None,
        'persistence_success_rate': persistence/total if total else None,
        'avg_latency': latency
    }

pre_m = compute_metrics(pre)
post_m = compute_metrics(post)
md = []
md.append('# Comparison Report')
md.append('## Pre-Feature Metrics')
md.append(str(pre_m))
md.append('## Post-Feature Metrics')
md.append(str(post_m))
metrics = { 'pre': pre_m, 'post': post_m }
open('results/aggregated_metrics.json','w').write(json.dumps(metrics, indent=2))
open(out_md, 'w').write('\n\n'.join(md))
print('Wrote', out_md)
