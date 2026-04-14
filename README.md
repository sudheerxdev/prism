# Prism: Multi-Agent Feedback Intelligence System

Transform messy team feedback into structured, actionable work items using AI agents.

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## What is Prism?

Prism is a **multi-agent LLM workflow system** that automates the chaos of team feedback management. Instead of manually triaging Slack messages, Discord threads, and chaotic voice notes, Prism:

1. **Ingests** raw messages from Discord, Slack, or manual input
2. **Classifies** them into semantic lanes (Bug, Feature, Idea, Marketing)
3. **Interprets** ambiguous requests into structured issue cards
4. **Architects** technical implementation plans automatically
5. **Organizes** everything in a beautiful, Linear-inspired kanban board

Perfect for **product teams, engineering teams, or anyone drowning in unstructured feedback**.

---

## Quick Start (5 minutes)

### Requirements
- Python 3.10+
- pip

### Installation

```bash
# Clone and enter directory
git clone <repo> && cd completedv_hack

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from queue_store import init_db; init_db()"

# Run the app
python -m streamlit run app.py
```

The app will open at **http://localhost:3002** (or check terminal output).

---

## Features

### 📥 Intake Queue
- Drag messages from Discord, Slack, or paste manually
- Auto-deduplication (no duplicate processing)
- Real-time inbox view

### 🤖 AI Agents (Multi-Provider)
Three specialized LLM agents powered by your API key:

| Agent | Purpose | Output |
|-------|---------|--------|
| **Classifier** | Categorizes raw feedback by lane & priority | `{lane, title, priority, summary}` |
| **Issue Interpreter** | Extracts structured issue cards | Acceptance criteria, edge cases, clarifications |
| **Implementation Architect** | Generates technical implementation plans | Step-by-step tasks, testing checklist, risks |

### 🏗️ Multi-Lane Kanban
- **Issues** 🐛 — bugs, errors, production problems
- **Features** ✨ — new capabilities, improvements
- **Ideas** 💡 — explorations, experiments, early concepts
- **Marketing** 📣 — copy, campaigns, positioning, growth signals

Each lane has its own lifecycle (e.g., Issue: new → confirmed → in_progress → resolved)

### 🔗 Integrations
- **Discord** — Monitor channels, auto-ingest messages
- **Slack** — Socket Mode support (no public URL needed)
- **REST API** — Programmatic access to all features
- **Context Files** — Upload docs/specs for agent context (60KB max)

### 🎨 Design
- Dark theme inspired by Linear/GitHub
- Responsive sidebar navigation
- Real-time board stats
- Accessibility-first HTML

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Streamlit UI (app.py)                                  │
│  • Kanban board, inbox, settings                        │
│  • ~1500 lines, heavily styled                          │
└──────────────┬──────────────────────────────────────────┘
               │
               ├──── FastAPI Backend (server.py) ────────┐
               │     • REST API endpoints                │
               │     • 4-worker executor for LLM calls   │
               │                                         │
               └─────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   LangGraph         Integration Bots      SQLite DB
   Agents (3)        • Discord            • messages
   • Classifier      • Slack              • items
   • Interpreter     • WebSocket Mode     • config
   • Architect                            • context_files
```

---

## Configuration

### Set API Keys (In-App)
1. Open Prism at http://localhost:3002
2. Go to **Settings** (sidebar)
3. Enter your keys:
   - **LLM Provider**: OpenAI (`sk-...`) or Groq (`gsk_...`)
   - **Discord Token** (optional)
   - **Slack Tokens** (optional)

Keys are stored securely in SQLite, not in `.env` files.

### Discord Bot Setup
1. Create a Discord app at https://discord.com/developers/applications
2. Enable "Message Content Intent"
3. Copy bot token to Prism settings
4. Invite bot to your server with `messages:read` scope
5. In Prism settings, list channel IDs (comma-separated) to monitor

### Slack Bot Setup
1. Create a Slack app at https://api.slack.com/apps
2. Enable "Socket Mode"
3. Generate app token (starts with `xapp-`)
4. Copy bot token (`xoxb-...`)
5. Subscribe to `message.channels` events
6. Add to Prism settings

---

## Usage Example

### Scenario: Messy Slack Message
User posts in Slack:
```
"yo the login button is broken on mobile, can't type password, tried chrome and safari both suck 😩"
```

**Flow:**
1. ✅ Prism ingests → Inbox
2. 🤖 Click "Auto-Process" → Classifier runs
   - **Lane**: issue
   - **Priority**: critical
   - **Title**: "Mobile login field input broken (iOS/Android)"
3. 📋 Click "Generate Issue Card" → Interpreter runs
   - Extracts acceptance criteria
   - Suggests edge cases (landscape mode, autofill, etc.)
4. 🏗️ Click "Generate Plan" → Architect runs
   - "Step 1: Check browser DevTools for input blur events"
   - "Step 2: Verify keyboard handling in React form component"
   - "Testing: Test on actual iPhone/Android devices"

**Result**: Structured, ready to assign to dev. No ambiguity.

---

## API Endpoints

### Messages (Inbox)
```bash
GET /api/inbox                      # Get pending messages
POST /api/inbox                     # Add message
  { "content": "...", "source": "manual" }
DELETE /api/inbox/{id}              # Dismiss message
```

### Processing
```bash
POST /api/process/{id}              # Auto-classify a message
  { "api_key": "sk-..." }
```

### Board
```bash
GET /api/board?lane=issue           # Get items by lane
GET /api/item/{id}                  # Get item details
POST /api/item/{id}                 # Update item
PUT /api/item/{id}/issue-card       # Save issue card
PUT /api/item/{id}/tech-plan        # Save tech plan
```

---

## LLM Providers Supported

### OpenAI (GPT-4o)
- Key: `sk-...`
- Fast, accurate, $0.15 per execution

### Groq (Llama 3.3 70B)
- Key: `gsk_...`
- Free tier, ~0.5s response time

Switch providers anytime in Settings.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Database locked" errors
- SQLite is single-threaded — don't run multiple instances simultaneously
- For production, migrate to PostgreSQL

### Discord/Slack bot not connecting
1. Check tokens in Settings
2. Verify bot has message read permissions
3. Check channel IDs are correct (not channel names)
4. Review logs: `Settings → Bot Status`

### LLM calls timing out
- Groq free tier has rate limits (100 requests/min)
- Use OpenAI for higher throughput
- Increase timeout in `agent.py` if needed

---

## Project Statistics

| Metric | Value |
|--------|-------|
| **Total LOC** | ~2,835 |
| **Core Agents** | 3 (Classifier, Interpreter, Architect) |
| **Integrations** | 2 (Discord, Slack) |
| **UI Components** | Kanban, Inbox, Settings, Details |
| **Database Tables** | 3 (messages, config, context_files) |
| **API Endpoints** | 15+ |

---

## Development

### File Structure
```
.
├── app.py              # Streamlit UI (main entry point)
├── server.py           # FastAPI backend  
├── agent.py            # LangGraph agents & LLM logic
├── queue_store.py      # SQLite persistence & migrations
├── discord_bot.py      # Discord WebSocket client
├── slack_bot.py        # Slack Socket Mode client
├── requirements.txt    # Dependencies
└── specflow.db         # SQLite (auto-created)
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### Running Backend Only (No UI)
```bash
python -m uvicorn server:app --reload --port 8000
```

---

## Limitations & Future Work

### Current Limitations
- **SQLite**: Single-threaded, not suitable for >10 concurrent users
- **LLM cost**: Runs against external APIs (OpenAI/Groq)
- **No auth**: Assumes trusted network
- **Mobile UI**: Designed for desktop/tablet

### Roadmap
- [ ] PostgreSQL support
- [ ] User authentication & teams
- [ ] Mobile-responsive UI
- [ ] Webhooks for custom integrations
- [ ] Local LLM support (Ollama, LM Studio)
- [ ] Test suite (unit + integration)

---

## Contributing

Found a bug or have an idea? 
1. Test it locally
2. Create an issue with reproducible steps
3. Submit a PR with tests

---

## License

MIT — Use freely, including in production!

---

## Support

- 📧 Questions? Check the in-app Settings panel for troubleshooting
- 🐛 Found a bug? Open an issue with `[BUG]` prefix
- 💡 Feature request? Open an issue with `[FR]` prefix

---

**Built with ❤️ using LangGraph, Streamlit, and FastAPI**  
**Inspired by Linear and GitHub's intuitive design**

