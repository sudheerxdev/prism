"""
PRISM — AI-Powered Feedback Intelligence Platform
Streamlit Cloud Compatible Version
"""

import streamlit as st
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PRISM",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize database ───────────────────────────────────────────────────────
try:
    from queue_store import (
        init_db, add_message, get_messages, set_status, board_counts,
        get_items, get_item, update_item, delete_item,
        get_cfg, set_cfg, LANE_META, LANE_STATUSES,
    )
    init_db()
except Exception as e:
    st.error(f"❌ Failed to initialize database: {e}")
    st.stop()

# ── Import agent ─────────────────────────────────────────────────────────────
try:
    from agent import (
        build_interpreter_graph, build_architect_graph, auto_process, check_relevance,
    )
except Exception as e:
    st.error(f"❌ Failed to load agent: {e}")
    st.stop()

# ── Optional bot imports ──────────────────────────────────────────────────────
try:
    import discord_bot
except Exception:
    discord_bot = None

try:
    import slack_bot
except Exception:
    slack_bot = None

# ── Basic CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #FFFFFF;
    background: #0D0D0D;
}

.main {
    background: #0D0D0D !important;
    color: #FFFFFF;
}

/* Cards */
.card {
    background: #1A1A1A;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    color: #FFFFFF;
}

/* Buttons */
button {
    background: #5B63ED !important;
    color: white !important;
}

button:hover {
    background: #6B77E0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.detail_id = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔷 PRISM")
    st.markdown("AI-Powered Feedback Intelligence")
    
    # API Key
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        value=get_cfg("ai_api_key", ""),
    )
    if api_key:
        set_cfg("ai_api_key", api_key)
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Signals", "⚙️ Settings"],
        label_visibility="collapsed",
    )
    
    st.divider()
    
    # Stats
    counts = board_counts()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", counts.get("total_items", 0))
    with col2:
        st.metric("Pending", counts.get("pending_items", 0))

# ── Main content ──────────────────────────────────────────────────────────────
if page == "📊 Signals":
    st.markdown("# 📊 Signals Board")
    
    counts = board_counts()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🐛 Issues", counts.get("issue_items", 0))
    with col2:
        st.metric("✨ Features", counts.get("feature_items", 0))
    with col3:
        st.metric("💡 Ideas", counts.get("idea_items", 0))
    with col4:
        st.metric("📣 Marketing", counts.get("marketing_items", 0))
    with col5:
        st.metric("📥 Inbox", counts.get("unclassified_items", 0))
    
    st.divider()
    
    # Add message
    st.markdown("### ➕ Add Feedback")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        raw_text = st.text_area(
            "Feedback text",
            placeholder="Paste feedback, GitHub issue, Slack message...",
            label_visibility="collapsed",
        )
    with col2:
        channel = st.selectbox(
            "Channel",
            ["manual", "slack", "discord", "github", "email"],
            label_visibility="collapsed",
        )
    with col3:
        if st.button("Add", use_container_width=True, type="primary"):
            if raw_text:
                try:
                    add_message("manual", raw_text.strip(), channel=channel, author="You")
                    st.success("✅ Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.divider()
    
    # Messages
    st.markdown("### 📋 Recent Messages")
    messages = get_messages(limit=10)
    if messages:
        for msg in messages:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{msg.get('channel', 'unknown')}**: {msg.get('content', '')[:100]}")
                with col2:
                    st.caption(msg.get('status', 'pending'))
                with col3:
                    if st.button("View", key=f"msg_{msg['id']}"):
                        st.session_state.detail_id = msg['id']
    else:
        st.info("No messages yet. Add one above!")

elif page == "⚙️ Settings":
    st.markdown("# ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Configuration")
        if not api_key:
            st.warning("⚠️ OpenAI API key not configured. Add it in the sidebar.")
        else:
            st.success("✅ API key configured")
    
    with col2:
        st.markdown("### 📊 Statistics")
        counts = board_counts()
        st.json(counts)
    
    st.divider()
    
    st.markdown("### ℹ️ About")
    st.markdown("""
    **PRISM** is an AI-powered feedback intelligence platform built with:
    - LangGraph (multi-agent orchestration)
    - Streamlit (UI)
    - FastAPI (backend)
    - OpenAI GPT-4o (intelligence)
    
    Features:
    - 🤖 Multi-agent feedback classification
    - 📊 Real-time analytics
    - 🔍 Semantic search
    - ⚡ Workflow automation
    - 💬 AI chat assistant
    - 🔗 GitHub integration
    """)

st.divider()
st.caption("PRISM • AI-Powered Feedback Intelligence")
