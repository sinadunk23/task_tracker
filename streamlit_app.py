import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mastery Dashboard 2026", layout="wide", page_icon="🤖")

# --- DATABASE CONNECTION ---
# In Streamlit Cloud, set these in "Settings" -> "Secrets"
# [mongo]
# uri = "your_mongodb_atlas_connection_string"
@st.cache_resource
def init_connection():
    try:
        return pymongo.MongoClient(st.secrets["uri"])
    except:
        st.error("MongoDB Connection Failed. Check your Secrets!")
        return None

client = init_connection()
if client:
    db = client.goal_tracker
else:
    st.stop()

# --- APP NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["Dashboard & Trends", "Update Tasks", "Log Fitness/Finance"])

# --- 1. DASHBOARD & TRENDS ---
if menu == "Dashboard & Trends":
    st.title("🚀 2026 Progress Dashboard")
    
    # Task Progress Overview
    st.subheader("Goal Completion")
    tasks_cursor = list(db.tasks.find())
    if tasks_cursor:
        df_tasks = pd.DataFrame(tasks_cursor)
        cols = st.columns(3)
        for i, row in df_tasks.iterrows():
            with cols[i % 3]:
                st.write(f"**{row['goal_name']}**")
                st.progress(int(row['progress_value']))
                st.caption(f"Status: {row['status']} | {row['progress_value']}%")
    else:
        st.info("No tasks in database. Go to 'Update Tasks' to add your goals.")

    st.divider()

    # Trend Analytics
    st.subheader("📈 Quantitative Trends")
    history_cursor = list(db.history.find())
    if history_cursor:
        df_hist = pd.DataFrame(history_cursor)
        metric_choice = st.selectbox("Select Metric to View Trend", df_hist['metric'].unique())
        
        filtered_df = df_hist[df_hist['metric'] == metric_choice].sort_values("date")
        fig = px.line(filtered_df, x="date", y="value", markers=True, 
                      title=f"{metric_choice} Progression")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No history data yet. Log your first metric in the sidebar.")

# --- 2. UPDATE TASKS ---
elif menu == "Update Tasks":
    st.title("⚙️ Manage Your Goals")
    
    with st.form("add_task_form"):
        st.write("Add or Update a Goal")
        g_name = st.text_input("Goal Name (e.g., Learn C++)")
        g_cat = st.selectbox("Category", ["Tech", "Fitness", "Personal", "Finance"])
        g_prog = st.slider("Progress %", 0, 100, 0)
        g_status = st.selectbox("Status", ["Not Started", "In-Progress", "Halted", "Completed"])
        
        if st.form_submit_button("Save Goal"):
            db.tasks.update_one(
                {"goal_name": g_name},
                {"$set": {"category": g_cat, "progress_value": g_prog, "status": g_status}},
                upsert=True
            )
            st.success(f"Updated {g_name}!")

# --- 3. LOG FITNESS/FINANCE ---
elif menu == "Log Fitness/Finance":
    st.title("📝 Daily Logging")
    
    with st.form("log_metrics"):
        metric_type = st.selectbox("Metric Type", ["Bodyweight", "Bench Press", "Squat", "Savings", "Books Read"])
        metric_val = st.number_input("Value", step=0.1)
        log_date = st.date_input("Date", datetime.now())
        
        if st.form_submit_button("Log Metric"):
            db.history.insert_one({
                "date": pd.to_datetime(log_date),
                "metric": metric_type,
                "value": metric_val
            })
            st.success(f"Logged {metric_val} for {metric_type}!")
