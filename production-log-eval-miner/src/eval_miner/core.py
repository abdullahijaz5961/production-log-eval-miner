from __future__ import annotations
import hashlib,json,math,random,re,sqlite3,time
from pathlib import Path
EMAIL=re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}');PHONE=re.compile(r'\b(?:\+?\d[\d -]{7,}\d)\b')
def redact(s):return PHONE.sub('[PHONE]',EMAIL.sub('[EMAIL]',s))
def vec(s,size=96):
 v=[0.0]*size
 for t in re.findall(r'[a-z0-9]+',s.lower()):v[int(hashlib.md5(t.encode()).hexdigest(),16)%size]+=1
 n=math.sqrt(sum(x*x for x in v))or 1;return[x/n for x in v]
def sim(a,b):return sum(x*y for x,y in zip(a,b))
class EvalMiner:
 def __init__(self,path='runtime/evals.db'):
  Path(path).parent.mkdir(parents=True,exist_ok=True);self.db=sqlite3.connect(path,check_same_thread=False);self.db.row_factory=sqlite3.Row
  self.db.executescript('create table if not exists logs(id integer primary key,prompt text,response text,model text,feature text,feedback integer,retries integer,latency real,created real,hash text unique);create table if not exists cases(id integer primary key,prompt text,reference text,rubric text,category text,difficulty text,quality real,confidence real,status text,source_log integer,created real);create table if not exists runs(id integer primary key,model text,pass_rate real,details text,created real);');self.db.commit()
 def ingest(self,entries):
  added=0
  for x in entries:
   prompt=redact(x['prompt']);response=redact(x.get('response',''));h=hashlib.sha256(f'{prompt}|{response}'.encode()).hexdigest()
   try:self.db.execute('insert into logs(prompt,response,model,feature,feedback,retries,latency,created,hash) values(?,?,?,?,?,?,?,?,?)',(prompt,response,x.get('model','unknown'),x.get('feature','general'),x.get('feedback',0),x.get('retries',0),x.get('latency',0),x.get('timestamp',time.time()),h));added+=1
   except sqlite3.IntegrityError:pass
  self.db.commit();return added
 def sample(self,limit=100,mode='signal'):
  rows=[dict(r) for r in self.db.execute('select * from logs')]
  if mode=='signal':rows.sort(key=lambda x:(x['feedback']<0,x['retries'],x['latency']),reverse=True)
  elif mode=='random':random.Random(42).shuffle(rows)
  else:rows=sorted(rows,key=lambda x:(x['feature'],x['model']))
  return rows[:limit]
 def classify(self,p):
  x=p.lower();cat='technical' if any(k in x for k in ['error','code','api','bug']) else 'billing' if any(k in x for k in ['invoice','refund','charge']) else 'account' if any(k in x for k in ['login','password','account']) else 'general'
  diff='adversarial' if any(k in x for k in ['ignore previous','system prompt']) else 'hard' if len(x.split())>35 else 'moderate' if len(x.split())>12 else 'simple';return cat,diff
 def mine(self,limit=100):
  existing=[(r['id'],vec(r['prompt'])) for r in self.db.execute('select id,prompt from cases')];created=review=0
  for x in self.sample(limit):
   v=vec(x['prompt'])
   if any(sim(v,e)>0.92 for _,e in existing):continue
   cat,diff=self.classify(x['prompt']);quality=max(1,min(5,4+(x['feedback'] or 0)-x['retries']*.5));confidence=.93 if abs(x['feedback']) or x['retries'] else .72;status='approved' if confidence>=.9 else 'review'
   reference=x['response'] if quality>=4 else 'A corrected response should directly answer the request, avoid unsupported claims, and state uncertainty.';rubric=json.dumps({'must':['direct answer','no unsupported claims'],'must_not':['fabricated facts'],'expected_behaviour':'answer'})
   cur=self.db.execute('insert into cases(prompt,reference,rubric,category,difficulty,quality,confidence,status,source_log,created) values(?,?,?,?,?,?,?,?,?,?)',(x['prompt'],reference,rubric,cat,diff,quality,confidence,status,x['id'],time.time()));existing.append((cur.lastrowid,v));created+=1;review+=status=='review'
  self.db.commit();return {'created':created,'review_queue':review}
 def cases(self,status=None):
  q='select * from cases'+(' where status=?' if status else '');return [dict(r) for r in self.db.execute(q,(status,) if status else ())]
 def evaluate(self,model='mock'):
  cases=self.cases('approved');passes=sum(1 for c in cases if 'fabricated' not in c['reference'].lower());rate=passes/max(1,len(cases));self.db.execute('insert into runs(model,pass_rate,details,created) values(?,?,?,?)',(model,rate,json.dumps({'cases':len(cases),'passes':passes}),time.time()));self.db.commit();return {'model':model,'cases':len(cases),'pass_rate':rate}
def health_summary():return {'status':'ok','project':'Production Log Eval Miner'}
