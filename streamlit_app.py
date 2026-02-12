import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import plotly.express as px

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"])

client = init_connection()
db = client.goal_tracker

# --- UI SETUP ---
st.set_page_config(page_title="2026 Goal Dashboard", layout="wide")
st.title("🚀 2026 Mastery Dashboard")

# --- SIDEBAR: LOG PROGRESS ---
st.sidebar.header("Log Daily Progress")
with st.sidebar.form("log_form"):
    metric = st.selectbox("Metric", ["Bodyweight", "Bench Press", "Squat", "Savings"])
    val = st.number_input("Value")
    submitted = st.form_submit_button("Update History")
    
    if submitted:
        db.history.insert_one({"date": datetime.now(), "metric": metric, "value": val})
        st.success(f"Logged {metric}!")

# --- MAIN CONTENT: TASK TRACKER ---
st.subheader("Current Goal Status")
tasks = list(db.tasks.find())
df_tasks = pd.DataFrame(tasks)

if not df_tasks.empty:
    # Progress Bar Visualization
    for index, row in df_tasks.iterrows():
        st.write(f"**{row['goal_name']}** ({row['category']})")
        st.progress(row['progress_value'] / 100)
else:
    st.info("No tasks found. Add them to MongoDB to see progress.")

# --- TRENDS & ANALYTICS ---
st.divider()
st.subheader("📈 Trend Analysis")

history_data = list(db.history.find())
if history_data:
    df_hist = pd.DataFrame(history_data)
    selected_metric = st.selectbox("Select Metric to View Trend", df_hist['metric'].unique())
    
    filtered_df = df_hist[df_hist['metric'] == selected_metric]
    fig = px.line(filtered_df, x="date", y="value", title=f"{selected_metric} Over Time")
    st.plotly_chart(fig, use_container_width=True)
