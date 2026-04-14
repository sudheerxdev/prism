"""
PRISM — AI-Powered Feedback Intelligence Platform
Streamlit Cloud Ultra-Minimal Version
"""

import streamlit as st

# ── Page config (MUST BE FIRST) ────────────────────────────────────────────────
st.set_page_config(
    page_title="PRISM",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── MINIMAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main { background: #0D0D0D !important; }
button { background: #5B63ED !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔷 PRISM")
st.markdown("**AI-Powered Feedback Intelligence**")

# ── LAZY initialization - only on demand ────────────────────────────────────────
@st.cache_resource
def get_db():
    """Initialize database lazily"""
    try:
        from queue_store import (
            init_db, add_message, get_messages, set_status, board_counts,
            get_cfg, set_cfg,
        )
        init_db()
        return {
            "add_message": add_message, "get_messages": get_messages,
            "set_status": set_status, "board_counts": board_counts,
            "get_cfg": get_cfg, "set_cfg": set_cfg,
        }
    except Exception as e:
        return None

# ── Session state ──────────────────────────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized = True

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Navigation")
    page = st.radio("", ["📊 Signals", "⚙️ Settings"], label_visibility="collapsed")

# ── Main content ──────────────────────────────────────────────────────────────────
# Get DB only when rendering
db = get_db()

if not db:
    st.error("❌ Database initialization failed")
    st.info("Troubleshooting: Check your database permissions and try again")
    st.stop()

if page == "📊 Signals":
    st.markdown("## 📊 Signals Board")
    
    # Show stats
    counts = db["board_counts"]()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🐛 Issues", counts.get("issue_items", 0))
    with col2:
        st.metric("✨ Features", counts.get("feature_items", 0))
    with col3:
        st.metric("💡 Ideas", counts.get("idea_items", 0))
    with col4:
        st.metric("📣 Marketing", counts.get("marketing_items", 0))
    
    st.divider()
    
    # Add feedback
    st.markdown("### ➕ Add Feedback")
    col1, col2 = st.columns([4, 1])
    with col1:
        text = st.text_area("Feedback:", placeholder="Enter your feedback...", label_visibility="collapsed")
    with col2:
        if st.button("Add", use_container_width=True, type="primary"):
            if text:
                try:
                    db["add_message"]("manual", text.strip(), channel="manual", author="You")
                    st.success("✅ Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.divider()
    
    # Show messages
    st.markdown("### 📋 Recent Messages")
    messages = db["get_messages"](limit=10)
    if messages:
        for msg in messages:
            with st.container(border=True):
                st.write(f"**{msg.get('channel', 'unknown')}**: {msg.get('content', '')[:80]}")
    else:
        st.info("No messages yet")

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔐 API Configuration")
        api_key = db["get_cfg"]("ai_api_key", "")
        if not api_key:
            st.warning("⚠️ OpenAI API key not configured")
        else:
            st.success("✅ API key configured")
    
    with col2:
        st.markdown("### 📊 Statistics")
        counts = db["board_counts"]()
        st.json(counts)
    
    st.divider()
    st.markdown("### ℹ️ About PRISM")
    st.markdown("""
    **PRISM** transforms feedback chaos into clarity using AI agents.
    
    Built with: Streamlit, LangGraph, OpenAI GPT-4o
    """)

st.divider()
st.caption("PRISM • AI-Powered Feedback Intelligence")
