import argparse,json
from pathlib import Path
from .core import EvalMiner

def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);v=s.add_parser('serve');v.add_argument('--host',default='127.0.0.1');v.add_argument('--port',type=int,default=8613);i=s.add_parser('ingest');i.add_argument('file');mn=s.add_parser('mine');mn.add_argument('--limit',type=int,default=100);s.add_parser('evaluate')
 a=p.parse_args();m=EvalMiner()
 if a.cmd=='serve':import uvicorn;uvicorn.run('eval_miner.api:app',host=a.host,port=a.port)
 elif a.cmd=='ingest':print({'added':m.ingest([json.loads(x) for x in Path(a.file).read_text().splitlines() if x.strip()])})
 elif a.cmd=='mine':print(m.mine(a.limit))
 else:print(m.evaluate())
