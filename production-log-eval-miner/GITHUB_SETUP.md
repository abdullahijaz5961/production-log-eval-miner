# GitHub setup

Recommended repository name: `production-log-eval-miner`

```powershell
git init
git branch -M main
git add .
git commit -m "feat: launch Production Log Eval Miner"
git remote add origin https://github.com/abdullahijaz5961/production-log-eval-miner.git
git push -u origin main
```

After changing a file directly on GitHub, run `git pull origin main` before the next local push.
Never commit `.env`, credentials, customer data, private documents, or large model weights.
