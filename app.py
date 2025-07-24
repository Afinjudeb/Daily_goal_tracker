import streamlit as st
if "goal" not in st.session_state:
    st.session_state.goal = ""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime
import os

st.set_page_config(page_title="AI Accountability Partner", layout="centered")

st.title(" AI-Powered Accountability Partner Dashboard")

# Load your fixed dataset
df = pd.read_csv('cleaned_data.csv')
GOALS_FILE = "daily_goals.csv"


# Show available columns for debugging or confirmation
st.write("🧾 Columns in the dataset:", df.columns.tolist())

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Overview Section
st.subheader("📌 Overview")
st.write("Here’s a summary of your app usage and goal achievement.")

# Goal Achievement Bar Chart
st.markdown("####  Goal Achievement")
goal_counts = df['goal_achieved'].value_counts()
st.write(goal_counts)
st.bar_chart(goal_counts)

# App Usage Trend Over Time
st.markdown("####  App Usage Trend Over Time")
daily_usage = df.groupby('Date')['Duration_minutes'].sum()
st.line_chart(daily_usage)

# Progress Tracker
st.markdown("####  Progress Tracker")
total_time = df['Duration_minutes'].sum()
active_days = df['Date'].nunique()
avg_daily_time = total_time / active_days if active_days else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Time (mins)", f"{total_time:.0f}")
col2.metric("Active Days", active_days)
col3.metric("Avg Daily Time", f"{avg_daily_time:.1f} mins")

st.markdown("#### 🧠 Suggested Smart Nudges")
suggestions = []

if avg_daily_time > 180:
    suggestions.append("Consider taking short breaks to maintain focus.")
if df['App'].str.contains('YouTube', case=False).any():
    suggestions.append("Switch to LinkedIn after 30 mins on YouTube.")
if df['App'].str.contains('WhatsApp', case=False).any():
    suggestions.append("Try reducing WhatsApp usage during peak focus hours.")

if suggestions:
    for i, tip in enumerate(suggestions, 1):
        st.markdown(f"**{i}. {tip}**")
else:
    st.write("You're doing great! Keep it up.")


st.set_page_config(page_title="Daily Goal Tracker", layout="centered")

st.title(" Daily Goal Tracker")
st.write("Set and track your goals each day. Stay consistent!")

# File to store goals
GOALS_FILE = "daily_goals.csv"
today_date = datetime.now().strftime("%Y-%m-%d")

# --- Input today's goal ---
st.subheader(" Enter Your Goal for Today")
today_goal = st.text_input("What's your goal for today?")

if st.button("Save Goal"):
    if today_goal.strip() == "":
        st.warning("Please enter a goal before saving.")
    else:
        new_entry = pd.DataFrame([[today_date, today_goal.strip(), "Not Achieved"]],
                                 columns=["Date", "Goal", "Status"])
        
        if os.path.exists(GOALS_FILE):
            df = pd.read_csv(GOALS_FILE)
            
            if today_date in df["Date"].values:
                st.warning("You have already set a goal for today.")
            else:
                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_csv(GOALS_FILE, index=False)
                st.success("Goal saved successfully!")
        else:
            new_entry.to_csv(GOALS_FILE, index=False)
            st.success("Goal saved successfully!")

# --- Mark today's goal as achieved ---
st.subheader(" Is Today’s Goal Achieved")

if os.path.exists(GOALS_FILE):
    df = pd.read_csv(GOALS_FILE)

    # Check if today's goal exists
    if today_date in df["Date"].values:
        today_status = df.loc[df["Date"] == today_date, "Status"].values[0]

        if today_status == "Achieved":
            st.success(" You've already marked today's goal as achieved!")
        else:
            if st.button("Mark as Achieved"):
                df.loc[df["Date"] == today_date, "Status"] = "Achieved"
                df.to_csv(GOALS_FILE, index=False)
                st.success("Goal marked as achieved! ")
    else:
        st.info("You haven't set a goal for today yet.")

# --- Display past goals ---
st.subheader(" Your Goal History")

if os.path.exists(GOALS_FILE):
    df = pd.read_csv(GOALS_FILE)

    # Show ✅ and ❌ for status
    df_display = df.copy()
    df_display["Status"] = df_display["Status"].apply(
        lambda x: "✅ Achieved" if x == "Achieved" else "❌ Not Achieved"
    )

    st.dataframe(df_display[::-1], use_container_width=True)
else:
    st.info("No goals have been added yet.")

# Daily Encouragement
st.markdown("####  Daily Motivation")
st.markdown("""
Are you still in line with your goals? If you are, great job!  
If not, you know what to do.  
Keep pushing – consistency wins! 
""")
