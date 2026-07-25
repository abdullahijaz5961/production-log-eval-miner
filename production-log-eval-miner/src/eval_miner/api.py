from fastapi import FastAPI
from pydantic import BaseModel
from .core import EvalMiner,health_summary
app=FastAPI(title='Production Log Eval Miner');m=EvalMiner()
class Entry(BaseModel):prompt:str;response:str='';model:str='unknown';feature:str='general';feedback:int=0;retries:int=0;latency:float=0
@app.get('/health')
def health():return health_summary()
@app.post('/v1/logs')
def ingest(entries:list[Entry]):return {'added':m.ingest([x.model_dump() for x in entries])}
@app.post('/v1/mine')
def mine(limit:int=100):return m.mine(limit)
@app.get('/v1/cases')
def cases(status:str|None=None):return m.cases(status)
@app.post('/v1/evaluate')
def evaluate(model:str='mock'):return m.evaluate(model)
