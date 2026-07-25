from eval_miner.core import EvalMiner,redact

def test_redaction():assert '[EMAIL]' in redact('email me a@b.com')
def test_pipeline(tmp_path):
 m=EvalMiner(tmp_path/'e.db');assert m.ingest([{'prompt':'refund invoice','response':'ok','feedback':-1}])==1;r=m.mine();assert r['created']==1;assert m.cases()
