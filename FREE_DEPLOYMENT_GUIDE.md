# 🚀 FREE DEPLOYMENT GUIDE - PRISM

Deploy your Streamlit + FastAPI app **completely free** with these platforms.

---

## 🥇 OPTION 1: STREAMLIT CLOUD (RECOMMENDED - 100% FREE)

**Best For**: Your Streamlit app, zero cost, official platform  
**Cost**: Free forever  
**Deployment Time**: 2 minutes  
**Live URL**: `prism.streamlit.app`

### ✅ Why Streamlit Cloud?
- Made specifically for Streamlit apps
- Completely FREE (no credit card needed)
- Auto-deploys from GitHub
- Custom subdomain included
- Real analytics dashboard
- Community support

### 📋 STEP-BY-STEP DEPLOYMENT

#### Step 1: Push to GitHub
```bash
cd d:\completedv_hack

# Initialize Git (if not done)
git init
git add .
git commit -m "PRISM - Ready for Streamlit Cloud deployment"
git remote add origin https://github.com/YOUR_USERNAME/prism
git push -u origin main
```

#### Step 2: Create Streamlit Cloud Account
1. Go to: https://share.streamlit.io
2. Click "Sign Up"
3. Sign up with GitHub account
4. Authorize Streamlit to access your repos

#### Step 3: Deploy App
1. Click "New app" button
2. Select your repo: `prism`
3. Select branch: `main`
4. File path: `app.py`
5. Click "Deploy"

**That's it!** ✅ Your app goes live in ~1 minute

#### Step 4: Access Your App
- Your app URL: `https://prism.streamlit.app`
- Share this link with judges

---

## 🥈 OPTION 2: HUGGING FACE SPACES (FREE + BACKEND)

**Best For**: Full app (Streamlit UI + FastAPI backend)  
**Cost**: Free forever  
**Deployment Time**: 3 minutes  
**Backend Included**: Yes  
**Live URL**: `username-prism.hf.space`

### ✅ Why Hugging Face Spaces?
- Supports both Streamlit AND custom Python apps
- Completely FREE
- Can run both frontend + backend together
- Great for ML/AI projects
- Built-in RAM/CPU limits (generous free tier)

### 📋 STEP-BY-STEP DEPLOYMENT

#### Step 1: Create Hugging Face Account
1. Go to: https://huggingface.co/join
2. Sign up (free)
3. Verify email

#### Step 2: Create a Space
1. Go to: https://huggingface.co/spaces
2. Click "Create new Space"
3. **Space name**: `prism`
4. **Owner**: Your username
5. **Space type**: `Docker` (to run both Streamlit + FastAPI)
6. **Visibility**: `Public`
7. Click "Create Space"

#### Step 3: Push Your Code
```bash
cd d:\completedv_hack

# Initialize Hugging Face Git (if needed)
git lfs install

# Clone the space repo
huggingface-cli repo clone USERNAME/prism
cd prism

# Copy your code into this directory
# Then push
git add .
git commit -m "PRISM deployment"
git push
```

#### Step 4: Create Dockerfile (if not already there)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY . .

# Initialize database
RUN python -c "from queue_store import init_db; init_db()"

# Run both Streamlit and FastAPI
CMD streamlit run app.py &
    python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

#### Step 5: Wait for Deployment
- HF Spaces auto-deploys from your push
- Takes ~2-3 minutes
- Your app lives at: `https://username-prism.hf.space`

---

## 🥉 OPTION 3: RENDER.COM (FREE TIER)

**Best For**: Full-stack apps with free tier  
**Cost**: Free (with limitations)  
**Deployment Time**: 5 minutes  
**Live URL**: `prism-demo.onrender.com`

### ✅ Why Render?
- Real free tier (not trial)
- Supports Streamlit + FastAPI together
- Easy GitHub integration
- PostgreSQL database free
- Spins down on inactivity (free tier)

### 📋 QUICK DEPLOYMENT

1. Go to: https://render.com
2. Sign up → Connect GitHub
3. Click "New +" → "Web Service"
4. Select your `prism` repository
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: 
   ```
   streamlit run app.py --server.port 8501 &
   python -m uvicorn server:app --host 0.0.0.0 --port 8000
   ```
7. Click "Deploy"
8. Wait ~2-3 minutes

**Live at**: `https://prism-demo.onrender.com`

---

## 🌩️ OPTION 4: RAILWAY (MINIMAL COST - $5/month)

**Best For**: If you want guaranteed uptime  
**Cost**: $5/month ($60/year)  
**Deployment Time**: 3 minutes  
**Live URL**: `prism.railway.app`

Not free but super affordable. If you want guaranteed uptime after free trial, this is best.

---

## 📊 FREE PLATFORM COMPARISON

| Platform | Cost | UI/Backend | Setup Time | Link |
|----------|------|-----------|-----------|------|
| **Streamlit Cloud** | FREE ✅ | UI only | 2 min | streamlit.app |
| **HF Spaces** | FREE ✅ | Both | 3 min | hf.space |
| **Render** | FREE ✅ | Both | 5 min | render.com |
| **Railway** | $5/mo | Both | 3 min | railway.app |

---

## 🎯 RECOMMENDED PATH

### For Quickest Launch:
**Use Streamlit Cloud** (your UI is Streamlit, so perfect match)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "PRISM"
git push -u origin main

# 2. Go to streamlit.io
# 3. Deploy from GitHub
# 4. ✅ Done in 2 minutes!
```

### For Full App (UI + API):
**Use Hugging Face Spaces** (free backend support)

```bash
# Similar to above, but deploy to HF Spaces instead
# Supports full Docker deployment with both services
```

---

## ⚙️ ENVIRONMENT SETUP FOR DEPLOYMENT

### For Streamlit Cloud:
Create `.streamlit/secrets.toml` in your repo:
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-key-here"
DISCORD_TOKEN = "your-token"
SLACK_TOKEN = "your-token"
```

Then access in app.py:
```python
import streamlit as st
openai_key = st.secrets["OPENAI_API_KEY"]
```

### For Hugging Face Spaces:
Create `.env` file:
```
OPENAI_API_KEY=your-key-here
DISCORD_TOKEN=your-token
SLACK_TOKEN=your-token
DATABASE_URL=sqlite:///specflow.db
```

---

## 🔧 VERIFICATION CHECKLIST

Before deploying:

- [ ] `git init` + all files committed
- [ ] GitHub repo created and ready
- [ ] `requirements.txt` updated with all dependencies
- [ ] `app.py` runs locally: `streamlit run app.py`
- [ ] `Dockerfile` exists (for HF Spaces/Render)
- [ ] `database.db` created locally
- [ ] Environment variables documented
- [ ] API endpoints tested with FastAPI

---

## 🚀 QUICK DECISION TREE

**Are you deploying?**

```
Do you have a GitHub account?
├─ YES
│  ├─ Want fastest deployment?
│  │  └─> USE STREAMLIT CLOUD ✅ (2 min)
│  ├─ Want both UI + API running?
│  │  └─> USE HUGGING FACE SPACES ✅ (3 min)
│  └─ Want guaranteed uptime?
│     └─> USE RAILWAY ($5/mo)
│
└─ NO
   └─> Create GitHub account first (free)
       Then follow Streamlit Cloud path
```

---

## 📝 FINAL DEPLOYMENT CHECKLIST

**Choose one platform**:
- [ ] Streamlit Cloud (FASTEST)
- [ ] Hugging Face Spaces (FULL APP)
- [ ] Render (BALANCED)

**Do these steps**:
1. [ ] Create account on chosen platform
2. [ ] Push code to GitHub
3. [ ] Connect platform to GitHub repo
4. [ ] Deploy
5. [ ] Test live app
6. [ ] Share URL with judges

**Time to live: 2-5 minutes** ⚡

---

## 🆘 TROUBLESHOOTING

### Streamlit Cloud Issues

**"Module not found" error**:
```bash
# Make sure requirements.txt has all imports
pip freeze > requirements.txt
git add requirements.txt && git commit -m "Update deps" && git push
```

**App shows blank page**:
```bash
# Check logs in Streamlit Cloud console
# Usually means missing environment variables
# Add to .streamlit/secrets.toml
```

### HF Spaces Issues

**Dockerfile not building**:
- Make sure image name is correct
- Check `python:3.9-slim` syntax
- Verify all COPY paths exist

**Out of memory**:
- HF Spaces has 16GB limit
- If exceeding, optimize code or use Render

### General Issues

**PORT conflicts**:
- Streamlit uses 8501 by default
- FastAPI uses 8000 by default
- Don't change these in deployment

**Database issues**:
- Deploy creates fresh SQLite database
- First load will initialize schema
- Data persists in HF Spaces/Render

---

## 📞 SUPPORT LINKS

- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-cloud
- **HF Spaces**: https://huggingface.co/docs/hub/spaces
- **Render**: https://render.com/docs
- **Railway**: https://docs.railway.app

---

## 🎉 YOU'RE READY!

Your PRISM app is production-ready. Pick a platform and deploy within the next 5 minutes.

**Status: ✅ DEPLOYMENT-READY**

Choose platform → Push GitHub → Deploy → Live! 🚀
