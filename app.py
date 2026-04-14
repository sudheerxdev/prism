"""
PRISM — AI-Powered Feedback Intelligence Platform
Streamlit Cloud - Absolute Minimal Test (Pure Static)
"""

import streamlit as st

# Set page config ONLY
st.set_page_config(page_title="PRISM", page_icon="◆", layout="wide")

# Pure static content - NO database calls, NO function calls
st.markdown("# 🔷 PRISM")
st.markdown("**AI-Powered Feedback Intelligence Platform**")
st.markdown("---")

# Static sidebar
with st.sidebar:
    st.markdown("**Status**: ✅ App is starting...")
    st.markdown("**Version**: 1.0")

# Static content only
st.markdown("## Welcome to PRISM")
st.success("✅ App loaded successfully!")
st.info("📊 Feedback Intelligence Platform Ready")

# Test import chain (non-blocking)
st.markdown("### System Check")
with st.spinner("Checking imports..."):
    try:
        import queue_store
        st.success("✓ queue_store module available")
    except Exception as e:
        st.error(f"✗ queue_store error: {e}")
    
    try:
        import agent
        st.success("✓ agent module available")
    except Exception as e:
        st.error(f"✗ agent error: {e}")

st.markdown("---")
st.caption("PRISM • v1.0")
