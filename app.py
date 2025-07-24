import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from datetime import date, datetime
import random


st.set_page_config(page_title="AI Accountability Partner", layout="centered")


GOALS_FILE = "daily_goals.csv"
USAGE_FILE = "cleaned_data.csv"
today_date = date.today().isoformat()
current_hour = datetime.now().hour


if "goal" not in st.session_state:
    st.session_state.goal = ""
if "new_goal" not in st.session_state:
    st.session_state.new_goal = ""

# Load cleaned usage data
st.title(" AI-Powered Accountability Partner Dashboard")
if os.path.exists(USAGE_FILE):
    usage_df = pd.read_csv(USAGE_FILE)
    usage_df['Date'] = pd.to_datetime(usage_df['Date'])

    # Overview Section
    st.subheader("Overview")
    st.write("Here’s a summary of your app usage and goal achievement.")

    # Goal Achievement
    st.markdown("#### Goal Achievement")
    goal_counts = usage_df['goal_achieved'].value_counts()
    st.write(goal_counts)
    st.bar_chart(goal_counts)

    # Usage Trend
    st.markdown("#### App Usage Trend Over Time")
    daily_usage = usage_df.groupby('Date')['Duration_minutes'].sum()
    st.line_chart(daily_usage)

    # Progress Tracker
    st.markdown("#### Progress Tracker")
    total_time = usage_df['Duration_minutes'].sum()
    active_days = usage_df['Date'].nunique()
    avg_daily_time = total_time / active_days if active_days else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Time (mins)", f"{total_time:.0f}")
    col2.metric("Active Days", active_days)
    col3.metric("Avg Daily Time", f"{avg_daily_time:.1f} mins")

    # Smart Suggestions
    st.markdown("#### Suggested Smart Nudges")
    suggestions = []
    if avg_daily_time > 180:
        suggestions.append(" Consider taking short breaks to maintain focus.")
    if usage_df['App'].str.contains('YouTube', case=False).any():
        suggestions.append(" Switch to LinkedIn after 30 mins on YouTube.")
    if usage_df['App'].str.contains('WhatsApp', case=False).any():
        suggestions.append(" Try reducing WhatsApp usage during peak focus hours.")

    if suggestions:
        for i, tip in enumerate(suggestions, 1):
            st.markdown(f"**{i}. {tip}**")
    else:
        st.success("You're doing great! Keep it up.")
else:
    st.warning("No usage data found. Please upload your cleaned_data.csv file.")

#Daily Goal Tracker
st.title(" Daily Goal Tracker")
st.write("Set and track your goals each day. Stay consistent!")

#Load/Create Daily Goal Data
if os.path.exists(GOALS_FILE):
    goal_df = pd.read_csv(GOALS_FILE)
else:
    goal_df = pd.DataFrame(columns=["Date", "Goal", "Status"])

#Adding some motivational quotes
quotes = [
    "Small steps every day lead to big results.",
    "Start where you are. Use what you have. Do what you can.",
    "Your future self will thank you for what you do today.",
    "One goal a day keeps regret away.",
    "Discipline is choosing what you want most over what you want now.",
    "Today is your opportunity to build the tomorrow you want."
]
st.info( random.choice(quotes))


today_goals = goal_df[goal_df["Date"] == today_date]
if today_goals.empty and current_hour >= 12:
    st.warning(" It's already noon and you haven't set a goal. Add one now!")

goal_bank = [
    "Read for 30 minutes ",
    "Take a 10-minute mindful break ",
    "Plan your top 3 tasks for tomorrow ",
    "Declutter your workspace ",
    "Go for a 15-minute walk ",
    "Listen to a podcast ",
    "Stretch your body ",
    "Call someone you love "
]

# Simulate AI by rotating suggestions daily
suggested = goal_bank[hash(today_date) % len(goal_bank)]
st.markdown("**AI-Suggested Goal for Today:**")
st.info(suggested)
if st.button("Use Suggested Goal"):
    st.session_state['new_goal'] = suggested
    st.rerun()


# To add a New Goal
st.subheader(" Add a Goal for Today")
new_goal = st.text_input("What's one goal you want to add?", value=st.session_state.get('new_goal', ""))
if st.button("Save Goal"):
    if new_goal.strip() == "":
        st.warning("Please enter a goal before saving.")
    else:
        new_entry = pd.DataFrame([[today_date, new_goal.strip(), "Not Achieved"]], columns=["Date", "Goal", "Status"])
        goal_df = pd.concat([goal_df, new_entry], ignore_index=True)
        goal_df.to_csv(GOALS_FILE, index=False)
        st.success("Goal saved successfully!")
        st.session_state['new_goal'] = ""
        st.rerun()


st.subheader(" Mark or Manage Today’s Goals")
today_goals = goal_df[goal_df["Date"] == today_date]
# Smart reminder if yesterday’s goal was missed
yesterday_date = (date.today() - pd.Timedelta(days=1)).isoformat()
missed_yesterday = goal_df[(goal_df["Date"] == yesterday_date) & (goal_df["Status"] != "Achieved")]
if not missed_yesterday.empty:
    st.warning("⚠️ You missed a goal yesterday. Want to stay on track today?")


if not today_goals.empty:
    for i, row in today_goals.iterrows():
        col1, col2, col3, col4 = st.columns([3, 1.2, 1.2, 1.2])
        with col1:
            st.write(f" {row['Goal']}")
        with col2:
            if row["Status"] != "Achieved":
                if st.button(f"✅ Achieve #{i}"):
                    goal_df.at[i, "Status"] = "Achieved"
                    goal_df.to_csv(GOALS_FILE, index=False)
                    st.success("Marked as Achieved!")
                    st.rerun()
            else:
                st.success("Achieved")
        with col3:
            if st.button(f" Edit #{i}"):
                new_text = st.text_input(f"Edit Goal #{i}", value=row["Goal"], key=f"edit_{i}")
                if st.button(f"Save Edit #{i}"):
                    goal_df.at[i, "Goal"] = new_text
                    goal_df.to_csv(GOALS_FILE, index=False)
                    st.success("Goal updated!")
                    st.rerun()
        with col4:
            if st.button(f" Delete #{i}"):
                goal_df.drop(index=i, inplace=True)
                goal_df.to_csv(GOALS_FILE, index=False)
                st.warning("Goal deleted.")
                st.rerun()
else:
    st.info("You haven't added any goals for today yet.")


st.subheader(" Your Goal History")
if not goal_df.empty:
    df_sorted = goal_df.sort_values(by="Date", ascending=False)
    grouped = df_sorted.groupby("Date")

    for date_, goals in grouped:
        st.markdown(f"###  {date_}")
        for _, row in goals.iterrows():
            status = "✅" if row["Status"] == "Achieved" else "❌"
            st.markdown(f"{status} {row['Goal']}")
        st.markdown("---")
else:
    st.info("No goals saved yet.")

if not today_goals.empty and all(today_goals["Status"] == "Achieved"):
    st.success("🔥 You’re crushing it today. Keep going!")
elif today_goals.empty:
    st.info("⏳ No goal set yet. Add one and take control of your day.")
else:
    st.warning("⏱️ Some goals are still pending. You got this!")


# For Daily Encouragement
st.markdown("####  Daily Motivation")
st.markdown("""
Are you still in line with your goals? If you are, great job!
If not, you know what to do.
Keep pushing – consistency wins!
""")
