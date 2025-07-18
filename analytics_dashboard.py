import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import StringIO

st.set_page_config(page_title="Guardrails Analytics Dashboard", layout="wide")
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

ANALYTICS_FILE = "test_analytics.json"
CURRENT_TEST_FILE = "charts/current_test_summary.json"

# --- Load Data ---
def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        st.error(f"Analytics file {ANALYTICS_FILE} not found!")
        return None
    with open(ANALYTICS_FILE, 'r') as f:
        return json.load(f)

def load_current_test():
    if not os.path.exists(CURRENT_TEST_FILE):
        return None
    with open(CURRENT_TEST_FILE, 'r') as f:
        return json.load(f)

data = load_analytics()
current = load_current_test()

# --- Helper: Download buttons ---
def download_button(label, data, file_name, mime):
    st.download_button(label, data, file_name=file_name, mime=mime)

# --- Helper: Last updated ---
def last_updated(path):
    if os.path.exists(path):
        ts = datetime.fromtimestamp(os.path.getmtime(path))
        return ts.strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"

# --- Main Layout ---
st.title("🛡️ Guardrails Analytics Dashboard")
st.caption("A modern, interactive dashboard for your rule-based guardrails system.")

# --- Top Metrics ---
with st.container():
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    if current:
        m = current['metrics']
        col1.metric("True Positives", m['True Positives'])
        col2.metric("True Negatives", m['True Negatives'])
        col3.metric("False Positives", m['False Positives'])
        col4.metric("False Negatives", m['False Negatives'])
        col5.metric("Success Rate", f"{current['success_rate']:.1f}%")
        if data:
            col6.metric("Block Rate", f"{(data.get('blocked_queries', 0) / max(data.get('total_queries', 1), 1)) * 100:.1f}%")
            col7.metric("Total Queries", data.get('total_queries', 0))
        else:
            col6.metric("Block Rate", "-")
            col7.metric("Total Queries", "-")
    elif data:
        col1.metric("Total Queries", data.get('total_queries', 0))
        col2.metric("Blocked Queries", data.get('blocked_queries', 0))
        col3.metric("Block Rate", f"{(data.get('blocked_queries', 0) / max(data.get('total_queries', 1), 1)) * 100:.1f}%")
        col4.metric("True Positives", data.get('true_positives', 0))
        col5.metric("True Negatives", data.get('true_negatives', 0))
        col6.metric("False Positives", data.get('false_positives', 0))
        col7.metric("False Negatives", data.get('false_negatives', 0))
    else:
        col1.metric("No Data", "-")

st.markdown(f"<div style='text-align:right; color:gray; font-size:0.9em;'>Last updated: {last_updated(ANALYTICS_FILE)}</div>", unsafe_allow_html=True)

# --- Tabs ---
tabs = st.tabs(["Current Test Run", "Overall Analytics", "Tables", "About"])

# --- Tab 1: Current Test Run ---
with tabs[0]:
    st.subheader("Current Test Run")
    if not current:
        st.info("No current test summary found. Run the test system to generate analytics.")
    else:
        m = current['metrics']
        precision = current['precision']
        recall = current['recall']
        f1_score = current['f1_score']
        total = current['total_tests']
        success_rate = current['success_rate']
        # 2x2 grid
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Confusion Matrix**")
            fig, ax = plt.subplots(figsize=(4, 3))
            cm = np.array([
                [m['True Negatives'], m['False Positives']],
                [m['False Negatives'], m['True Positives']]
            ])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                        xticklabels=['Predicted Safe', 'Predicted Harmful'],
                        yticklabels=['Actual Safe', 'Actual Harmful'], ax=ax)
            st.pyplot(fig, use_container_width=True)
        with c2:
            st.markdown("**Performance Metrics**")
            fig, ax = plt.subplots(figsize=(4, 3))
            bars = ax.bar(m.keys(), m.values(), color=['#2ecc71', '#3498db', '#e74c3c', '#f39c12'])
            for bar, value in zip(bars, m.values()):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(value), ha='center', va='bottom', fontweight='bold')
            ax.set_ylabel('Count')
            st.pyplot(fig, use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Success vs Failure Rate**")
            fig, ax = plt.subplots(figsize=(4, 3))
            success = m['True Positives'] + m['True Negatives']
            failure = m['False Positives'] + m['False Negatives']
            ax.pie([success, failure], labels=['Success', 'Failure'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
            st.pyplot(fig, use_container_width=True)
        with c4:
            st.markdown("**Precision, Recall, F1-Score**")
            fig, ax = plt.subplots(figsize=(4, 3))
            scores = [precision, recall, f1_score]
            score_labels = ['Precision', 'Recall', 'F1-Score']
            bars = ax.bar(score_labels, scores, color=['#9b59b6', '#e67e22', '#1abc9c'])
            for bar, score in zip(bars, scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
            ax.set_ylim(0, 1)
            st.pyplot(fig, use_container_width=True)
        with st.expander("Show raw current test summary JSON"):
            st.json(current)
        st.markdown("---")
        download_button("Download Current Test Summary (JSON)", json.dumps(current, indent=2), "current_test_summary.json", "application/json")

# --- Tab 2: Overall Analytics ---
with tabs[1]:
    st.subheader("Overall Analytics")
    if not data:
        st.warning("No analytics data found. Run the test system to generate analytics.")
    else:
        # 2x2 grid
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Query Volume Over Time**")
            if 'session_data' in data and data['session_data']:
                df = pd.DataFrame(data['session_data'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                daily_counts = df.groupby('date').size()
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=6)
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Queries')
                ax.tick_params(axis='x', rotation=45)
                st.pyplot(fig, use_container_width=True)
        with c2:
            st.markdown("**Queries by Category**")
            if 'categories_blocked' in data:
                categories = list(data['categories_blocked'].keys())
                counts = list(data['categories_blocked'].values())
                sorted_data = sorted(zip(categories, counts), key=lambda x: x[1], reverse=True)
                categories, counts = zip(*sorted_data)
                fig, ax = plt.subplots(figsize=(4, 3))
                bars = ax.barh(categories, counts, color=sns.color_palette("husl", len(categories)))
                for i, (bar, count) in enumerate(zip(bars, counts)):
                    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(count), ha='left', va='center', fontweight='bold')
                ax.set_xlabel('Count')
                st.pyplot(fig, use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Risk Level Distribution**")
            if 'risk_levels' in data:
                risk_levels = list(data['risk_levels'].keys())
                risk_counts = list(data['risk_levels'].values())
                fig, ax = plt.subplots(figsize=(4, 3))
                colors = ['#2ecc71', '#f39c12', '#e74c3c']
                ax.pie(risk_counts, labels=risk_levels, autopct='%1.1f%%', colors=colors)
                st.pyplot(fig, use_container_width=True)
        with c4:
            st.markdown("**Daily Block Rate (%)**")
            if 'session_data' in data and data['session_data']:
                df = pd.DataFrame(data['session_data'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                daily_metrics = df.groupby('date').agg({'blocked': ['sum', 'count']}).reset_index()
                daily_metrics.columns = ['date', 'blocked_count', 'total_count']
                daily_metrics['block_rate'] = (daily_metrics['blocked_count'] / daily_metrics['total_count']) * 100
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.plot(daily_metrics['date'], daily_metrics['block_rate'], marker='s', linewidth=2, markersize=6, color='#e74c3c')
                ax.set_xlabel('Date')
                ax.set_ylabel('Block Rate (%)')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
                st.pyplot(fig, use_container_width=True)
        with st.expander("Show raw analytics JSON"):
            st.json(data)
        st.markdown("---")
        download_button("Download Analytics (JSON)", json.dumps(data, indent=2), "test_analytics.json", "application/json")

# --- Tab 3: Tables ---
with tabs[2]:
    st.subheader("Analytics Tables")
    if not data:
        st.warning("No analytics data found.")
    else:
        st.markdown("**Category Analysis Table**")
        if 'categories_blocked' in data:
            cat_df = pd.DataFrame(list(data['categories_blocked'].items()), columns=['Category', 'Blocked Count'])
            st.dataframe(cat_df)
        st.markdown("**Risk Level Analysis Table**")
        if 'risk_levels' in data:
            risk_df = pd.DataFrame(list(data['risk_levels'].items()), columns=['Risk Level', 'Count'])
            st.dataframe(risk_df)
        st.markdown("**Session Data Table**")
        if 'session_data' in data:
            df = pd.DataFrame(data['session_data'])
            st.dataframe(df)
        st.markdown("---")
        # Download as CSV
        if 'session_data' in data:
            csv_buffer = StringIO()
            pd.DataFrame(data['session_data']).to_csv(csv_buffer, index=False)
            download_button("Download Session Data (CSV)", csv_buffer.getvalue(), "session_data.csv", "text/csv")

# --- Tab 4: About/Help ---
with tabs[3]:
    st.subheader("About & Help")
    st.markdown("""
    **Guardrails Analytics Dashboard**
    
    - **Current Test Run:** Shows metrics and charts for the most recent test run.
    - **Overall Analytics:** Shows all-time analytics, trends, and breakdowns.
    - **Tables:** View and download raw analytics data.
    - **Download:** Use the download buttons to export analytics for further analysis.
    
    **Legend:**
    - **True Positive:** Harmful query correctly blocked
    - **True Negative:** Safe query correctly allowed
    - **False Positive:** Safe query incorrectly blocked
    - **False Negative:** Harmful query incorrectly allowed
    
    **How to use:**
    1. Run your test system to generate analytics.
    2. Run this dashboard: `streamlit run analytics_dashboard.py`
    3. Explore all tabs for a complete view of your system's performance.
    
    _Made with ❤️ using Streamlit, Matplotlib, Seaborn, and Pandas._
    """) 