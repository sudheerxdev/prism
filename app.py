"""
PRISM — AI-Powered Feedback Intelligence Platform
Streamlit Cloud - True Lazy Initialization (NO module-level DB calls)
"""

import streamlit as st

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: ABSOLUTE BARE MINIMUM (page config + CSS only)
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="PRISM", page_icon="◆", layout="wide")

st.markdown("""
<style>
.main { background: #0D0D0D !important; color: #FFF; }
button { background: #5B63ED !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔷 PRISM")
st.markdown("**AI-Powered Feedback Intelligence**")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: LAZY DB function (DEFINED but NEVER called at module level)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def _get_db():
    """Initialize database lazily - ONLY called when explicitly needed"""
    try:
        from queue_store import (
            init_db, add_message, get_messages, board_counts, get_cfg, set_cfg
        )
        init_db()
        return {
            "add": add_message,
            "get": get_messages,
            "counts": board_counts,
            "get_cfg": get_cfg,
            "set_cfg": set_cfg,
        }
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: Navigation (safe - no function calls, just UI)
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("**Navigation**")
    page = st.radio("", ["📊 Board", "⚙️ Settings"], label_visibility="collapsed")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: Page rendering (DB initialization happens HERE, inside conditionals)
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📊 Board":
    st.markdown("## 📊 Signals Board")
    
    # NOW initialize DB (only when rendering this page)
    db = _get_db()
    
    if not db:
        st.error("❌ Unable to initialize database")
        st.stop()
    
    # Show statistics
    counts = db["counts"]()
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
    
    # Add feedback form
    st.markdown("### ➕ Add Feedback")
    col1, col2 = st.columns([4, 1])
    with col1:
        text = st.text_area(
            "Your feedback:",
            placeholder="Type or paste feedback...",
            label_visibility="collapsed",
            key="feedback_input"
        )
    with col2:
        if st.button("Add", use_container_width=True, type="primary"):
            if text.strip():
                try:
                    db["add"]("manual", text.strip(), channel="manual", author="User")
                    st.success("✅ Added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.divider()
    
    # Show recent messages
    st.markdown("### 📋 Recent Feedback")
    messages = db["get"](limit=10)
    if messages:
        for msg in messages:
            st.info(f"**{msg.get('channel', 'manual')}**: {msg.get('content', '')[:80]}")
    else:
        st.info("No feedback yet. Add some above! ⬆️")

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    
    # Initialize DB for settings page
    db = _get_db()
    
    if not db:
        st.error("❌ Unable to initialize database")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 API Configuration")
        api_key = db["get_cfg"]("ai_api_key", "")
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ No API key configured")
    
    with col2:
        st.markdown("### 📊 Board Statistics")
        counts = db["counts"]()
        st.json({
            "Total Items": counts.get("total_items", 0),
            "Pending": counts.get("pending_items", 0),
            "Issues": counts.get("issue_items", 0),
            "Features": counts.get("feature_items", 0),
        })

st.divider()
st.caption("PRISM • AI-Powered Feedback Intelligence • v1.0")
