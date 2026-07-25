import json
from eval_miner.core import EvalMiner
m=EvalMiner();entries=[json.loads(x) for x in open('data/production_logs.jsonl',encoding='utf-8')];print({'ingested':m.ingest(entries),**m.mine(200),**m.evaluate()})
