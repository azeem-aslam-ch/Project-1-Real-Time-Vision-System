import streamlit as st
import requests
import time
import pandas as pd
from PIL import Image
import io
import os

# Setup Configuration
# For local Docker: http://api_service:8000
# For cloud: link to your public backend URL
API_URL = os.environ.get("API_URL", "http://api_service:8000")
API_KEY = os.environ.get("API_KEY", "dev-key-123")

st.set_page_config(page_title="Vision Platform Dashboard", layout="wide")

st.title("🚀 Real-Time Vision Detection Platform")
st.sidebar.title("Control Panel")

# Header Auth
headers = {"X-API-Key": API_KEY}

def get_status():
    try:
        r = requests.get(f"{API_URL}/status", headers=headers, timeout=1)
        return r.json()
    except:
        return {"status": "OFFLINE"}

def get_metrics():
    try:
        r = requests.get(f"{API_URL}/metrics", headers=headers, timeout=1)
        return r.json()
    except:
        return {}

def get_events():
    try:
        r = requests.get(f"{API_URL}/events", headers=headers, timeout=1)
        return r.json()
    except:
        return []

# Sidebar Controls
status = get_status()
st.sidebar.metric("System Status", status.get("status", "UNKNOWN"))
st.sidebar.text(f"Source: {status.get('source', 'N/A')}")

if st.sidebar.button("Reload Config"):
    requests.post(f"{API_URL}/reload_config", headers=headers)
    st.sidebar.success("Reload sent")

def get_latest_frame_data():
    try:
        r = requests.get(f"{API_URL}/latest_frame", headers=headers, timeout=1)
        if r.status_code == 200:
            return r.content
    except:
        return None

# Main Layout: 2 Columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Feed")
    frame_data = get_latest_frame_data()
    if frame_data:
        st.image(frame_data, use_container_width=True)
    else:
        st.error("Live feed offline")

with col2:
    st.subheader("Performance Metrics")
    metrics = get_metrics()
    if metrics:
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("FPS", metrics.get("fps", 0))
        m_col2.metric("Proc Latency", f"{metrics.get('total_latency', 0)}ms")
        
        # Simple gauge chart for latency
        st.progress(min(metrics.get("total_latency", 0) / 200, 1.0), text="Inference Saturation")
    
    st.subheader("Recent Events")
    events = get_events()
    if events:
        df = pd.DataFrame(events)
        st.table(df)
    else:
        st.info("No events detected yet.")

# Auto-refresh logic
time.sleep(1)
st.rerun()
