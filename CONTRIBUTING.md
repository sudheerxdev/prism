# Contributing to Prism

Thanks for your interest in contributing! This guide will help you get started.

## Getting Started

### 1. Clone & Setup
```bash
git clone <repo>
cd completedv_hack
pip install -r requirements.txt
pip install pytest pytest-cov  # for testing
```

### 2. Initialize Database
```bash
python -c "from queue_store import init_db; init_db()"
```

### 3. Run Tests
```bash
python -m pytest tests/ -v
```

### 4. Run Locally
```bash
python -m streamlit run app.py
```

## Project Structure

```
├── app.py              # Streamlit UI
├── server.py           # FastAPI backend
├── agent.py            # LangGraph agents
├── queue_store.py      # Database layer
├── discord_bot.py      # Discord integration
├── slack_bot.py        # Slack integration
├── tests/              # Test suite
├── Dockerfile          # Docker configuration
└── requirements.txt    # Dependencies
```

## Code Style

- **Python**: PEP 8, type hints where possible
- **Line length**: 100 chars max
- **Naming**: 
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPERCASE`

Example:
```python
from typing import Optional

def classify_feedback(content: str, threshold: float = 0.8) -> Optional[str]:
    """Classify a message into a lane.
    
    Args:
        content: The raw message text
        threshold: Confidence threshold (0-1)
    
    Returns:
        Lane name ('issue', 'feature', 'idea', 'marketing') or None
    """
    pass
```

## Making Changes

### 1. Create a Branch
```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bug
```

### 2. Make Changes
- Keep commits small and focused
- Write clear commit messages (e.g., "Add dark mode toggle to settings")
- Add tests for new functionality

### 3. Test Locally
```bash
python -m pytest tests/ -v --cov=.
```

### 4. Submit a Pull Request
- Reference any related issues (#123)
- Describe what changed and why
- Ensure all tests pass

## Areas for Contribution

### High Priority
- [ ] Test coverage (currently ~0%)
- [ ] Error handling in LLM calls
- [ ] API input validation
- [ ] Database migration tooling

### Medium Priority
- [ ] PostgreSQL support
- [ ] User authentication
- [ ] Rate limiting
- [ ] Caching for LLM responses

### Low Priority
- [ ] Mobile responsive design
- [ ] Dark mode toggle (UI already supports it)
- [ ] WebSocket support for real-time updates
- [ ] Local LLM integrations

## Reporting Bugs

Found a bug? Please:

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title (e.g., "Discord bot stops after 1 hour")
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version, OS, and dependency versions
   - (Optional) error trace/logs

Example:
```
Title: [BUG] Duplicate messages not being deduplicated

Steps:
1. Add message "test" from Discord
2. Add same message "test" from Slack
3. Check inbox

Expected: Both appear (different sources)
Actual: Only one appears
```

## Feature Requests

Have an idea? Create an issue with `[FR]` prefix:

```
Title: [FR] Support for GitHub issue integration

Use case: We want to bridge GitHub issues into Prism
Benefit: Real-time GitHub notifications in kanban
```

## Testing

### Running Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_core.py -v

# Specific test function
python -m pytest tests/test_core.py::TestDatabase::test_add_message_succeeds -v

# With coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### Writing Tests

Tests should be in `tests/` directory, prefixed with `test_`:

```python
def test_classifier_recognizes_critical_bugs():
    """Test that critical-level bugs are classified correctly."""
    add_message("slack", "Production is down!", "general", "user")
    msg = get_messages("pending")[0]
    
    classify_item(msg["id"], "issue", "Production down", "...", "critical")
    
    item = get_item(msg["id"])
    assert item["priority"] == "critical"
```

## Documentation

- **In-code**: Use docstrings for functions/classes
- **README**: Update [README.md](README.md) for user-facing changes
- **Comments**: Explain *why*, not *what* (code shows "what")

Example:
```python
# ❌ Bad
x = y + 1  # Add 1 to y

# ✅ Good
next_item_id = current_id + 1  # Items have sequential IDs
```

## Commit Message Guidelines

```
<type>: <subject>

<body>

<footer>
```

Examples:
```
feat: Add PostgreSQL support

- Migrate from SQLite to PostgreSQL for scalability
- Keep SQLite as fallback for local dev
- Add POSTGRES_URL environment variable

Closes #42
```

```
fix: Prevent Discord bot timeout after 1 hour

Use heartbeat mechanism to keep WebSocket connection alive

Fixes #128
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

## Questions?

- 📧 Email: Check repo for contact
- 💬 Discussions: GitHub Discussions (if enabled)
- 🐛 Issues: Use GitHub Issues for bug reports

Thanks for contributing! 🙌
