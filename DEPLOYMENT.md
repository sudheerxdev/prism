# Deployment Guide

Deploy Prism to production or cloud environments in minutes.

## Local Development

### Quick Start (Simplest)

```bash
# 1. Clone
git clone <repo> && cd completedv_hack

# 2. Install
pip install -r requirements.txt

# 3. Run
python -m streamlit run app.py
```

Visit **http://localhost:3002**

### With Tests

```bash
pip install -r requirements.txt pytest

# Initialize DB
python -c "from queue_store import init_db; init_db()"

# Run tests
python -m pytest tests/ -v
```

Expected output: **22 tests passed** ✅

---

## Docker (Single Container)

Perfect for judges who want to try it immediately.

### Build & Run

```bash
# Build image
docker build -t prism .

# Run container
docker run -p 3002:3002 \
  -e OPENAI_API_KEY=sk-your-key \
  prism
```

Visit **http://localhost:3002**

### Troubleshooting Docker

```bash
# View logs
docker logs <container_id>

# Enter container
docker exec -it <container_id> bash

# Rebuild without cache
docker build --no-cache -t prism .
```

---

## Docker Compose (Full Stack)

Best for local development with persistent data.

### Quick Start

```bash
# Copy env template
cp .env.example .env

# Edit .env with your keys
nano .env  # or use your editor

# Start
docker-compose up
```

Visit **http://localhost:3002**

### Using with Environment Variables

```bash
# Without .env file
OPENAI_API_KEY=sk-... DISCORD_TOKEN=... docker-compose up

# Or inline
docker-compose -e OPENAI_API_KEY=sk-... up
```

### Persistent Data

Database is stored in `specflow.db` (mounted volume).

```bash
# Inspect database
sqlite3 specflow.db

# Backup
cp specflow.db specflow.db.backup

# Restore
cp specflow.db.backup specflow.db
```

### Stop & Clean Up

```bash
# Stop containers
docker-compose down

# Remove everything (including volumes)
docker-compose down -v
```

---

## Cloud Deployment

### Heroku (Easiest)

1. **Create account** at https://heroku.com

2. **Create Heroku app**
```bash
heroku create my-prism-app
```

3. **Set environment variables**
```bash
heroku config:set OPENAI_API_KEY=sk-your-key
heroku config:set DISCORD_TOKEN=your-token
heroku config:set SLACK_BOT_TOKEN=your-slack-token
heroku config:set SLACK_APP_TOKEN=your-app-token
```

4. **Deploy** (requires `Procfile`)
```bash
git push heroku main
```

5. **View logs**
```bash
heroku logs --tail
```

**Issue**: Heroku doesn't include Dockerfile support in free tier. Skip to **Railway** or **Render** instead.

---

### Railway.app (Recommended for Hackathons)

Fast, simple, generous free tier.

1. **Sign up** at https://railway.app

2. **Connect GitHub** (or push code manually)

3. **Create new project** → Select your repo

4. **Configure services**:
   - Name: `prism`
   - Dockerfile: `./Dockerfile`
   - Port: `3002`

5. **Add environment variables**:
   ```
   OPENAI_API_KEY=sk-your-key
   DISCORD_TOKEN=xxx
   SLACK_BOT_TOKEN=xxx
   SLACK_APP_TOKEN=xxx
   ```

6. **Deploy** (automatic on push)

6. Visit your Railway domain

---

### Render.com

Another great free-tier option.

1. **Sign up** at https://render.com

2. **Create new Web Service**
   - Connect GitHub
   - Select repo
   - Environment: Docker
   - Region: US
   - Plan: Free

3. **Set environment variables** in dashboard

4. **Deploy**

---

### AWS ECS (Production)

For enterprise deployments.

```bash
# Authenticate with AWS ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

# Tag image
docker tag prism:latest <account>.dkr.ecr.<region>.amazonaws.com/prism:latest

# Push to ECR
docker push <account>.dkr.ecr.<region>.amazonaws.com/prism:latest

# Create ECS task definition, service, etc.
# (See AWS documentation for details)
```

---

## Environment Variables

Required and optional configuration:

| Variable | Required | Example |
|----------|----------|---------|
| `OPENAI_API_KEY` | ✅ Yes (or Groq key) | `sk-...` |
| `DISCORD_TOKEN` | ❌ No | Your bot token |
| `SLACK_BOT_TOKEN` | ❌ No | `xoxb-...` |
| `SLACK_APP_TOKEN` | ❌ No | `xapp-...` |

**Note**: You can also set these **in the app UI** (Settings page). They'll be saved to SQLite.

## Database Migration

### Backup SQLite

```bash
cp specflow.db specflow.db.backup
```

### Migrate to PostgreSQL (Future)

```bash
# Export SQLite
sqlite3 specflow.db .dump > dump.sql

# Import to PostgreSQL
psql -U postgres prism < dump.sql
```

---

## Monitoring & Troubleshooting

### Check Application Health

```bash
# If deployed to Heroku/Railway
curl https://your-app.herokuapp.com/_stcore/health

# Local
curl http://localhost:3002/_stcore/health
```

### View Logs

**Heroku**:
```bash
heroku logs --tail
```

**Railway**:
```
View in dashboard → Logs tab
```

**Docker**:
```bash
docker logs -f <container_id>
```

### Common Issues

#### "ModuleNotFoundError: No module named 'streamlit'"
- Ensure `requirements.txt` is installed
- Rebuild Docker image if needed

#### "OPENAI_API_KEY not set"
- Set via environment variable or app Settings page
- Verify key format (starts with `sk-`)

#### "Discord bot not connecting"
- Check token is valid
- Verify bot has message intents enabled
- Check channel IDs in Settings

#### "Database locked" errors
- SQLite is single-threaded
- Don't run multiple instances simultaneously
- Consider PostgreSQL for production

---

## PostgreSQL Setup (Production Ready)

For deployments with >10 concurrent users.

```bash
# Install PostgreSQL
# (varies by OS)

# Create database
createdb prism

# Update connection string in settings
# (Replace SQLite with psycopg2 in queue_store.py)

# Run migrations
python -c "from queue_store import init_db; init_db()"
```

---

## Performance Tuning

### Optimize LLM Calls

```python
# In agent.py, increase temperature for faster/cheaper responses
return ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.3)
```

### Cache Responses

Add Redis caching to avoid redundant LLM calls:

```python
import redis

cache = redis.Redis(host='localhost', port=6379)

@cache.cache(ttl=3600)  # Cache for 1 hour
def classify_feedback(content: str):
    return classifier_agent(content)
```

### Database Indexes

For PostgreSQL:

```sql
CREATE INDEX idx_lane ON messages(lane);
CREATE INDEX idx_status ON messages(status);
CREATE INDEX idx_created ON messages(created_at);
```

---

## Backup Strategy

### Automated Daily Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
cp specflow.db backups/specflow_$DATE.db

# Keep last 30 days
find backups -name "specflow_*.db" -mtime +30 -delete
```

### Cloud Storage Backup

```bash
# Upload to S3
aws s3 cp specflow.db s3://my-backup-bucket/specflow.db

# Upload to Google Cloud
gsutil cp specflow.db gs://my-backup-bucket/specflow.db
```

---

## Security Checklist

- [ ] Set strong passwords for services (Discord, Slack, OpenAI)
- [ ] Use environment variables (not hardcoded keys)
- [ ] Enable HTTPS in production
- [ ] Restrict API access to trusted networks
- [ ] Rotate API keys regularly
- [ ] Back up database regularly
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated (`pip install --upgrade -r requirements.txt`)

---

## Next Steps

1. **Test locally** with Docker Compose
2. **Deploy to Railway/Render** for free tier
3. **Set up monitoring** with your cloud provider
4. **Configure backups** via cron or cloud storage
5. **Scale database** to PostgreSQL when needed

See [README.md](README.md) for more information.

