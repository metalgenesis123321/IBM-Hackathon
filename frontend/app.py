# frontend/app.py
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
import pandas as pd

from services import (
    get_actions,
    execute_action,
    execute_all_actions,
    simulate_meeting_end,
)

load_dotenv()

st.set_page_config(
    page_title="Autonomous Chief of Staff - Decision Board",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CUSTOM CSS (DARK THEME + IBM BLUE) ----------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* Global dark background + base text */
    body, .stApp {
        background: radial-gradient(circle at top left, #111827 0%, #020617 45%, #000000 100%) !important;
        color: #ffffff !important;
    }

    .main .block-container {
        background: #020617 !important;
        border-radius: 18px !important;
        padding: 2.2rem 3rem !important;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.65) !important;
        border: 1px solid rgba(15, 98, 254, 0.25) !important;
    }

    /* Make most text light by default */
    .main, .block-container, .stMarkdown, p, label, span, div {
        color: #e5e7eb !important;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #020617 50%, #020617 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.25) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] button {
        background: #0f62fe !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.7rem 1.6rem !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 24px rgba(15, 98, 254, 0.45) !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background: #0050d4 !important;
    }
    
    /* HEADINGS */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
    }
    
    h2 {
        color: #e5e7eb !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #0f62fe !important;
        font-weight: 600 !important;
    }

    /* CAPTIONS, SMALL TEXT */
    .stCaption, .st-emotion-cache-10trblm, .st-emotion-cache-1lb29wj {
        color: #9ca3af !important;
    }
    
    /* BUTTONS (main area) */
    .stButton > button[kind="primary"] {
        background: #0f62fe !important;
        color: #ffffff !important;
        border-radius: 999px !important;
        padding: 0.7rem 1.8rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        box-shadow: 0 12px 35px rgba(15, 98, 254, 0.55) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #0050d4 !important;
    }
    
    .stButton > button {
        background: #1f2937 !important;
        color: #e5e7eb !important;
        border-radius: 999px !important;
        padding: 0.7rem 1.8rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(148, 163, 184, 0.35) !important;
    }
    
    .stButton > button:hover {
        background: #111827 !important;
    }
    
    /* INFO / SUCCESS / ERROR BANNERS */
    .stSuccess {
        background: rgba(34, 197, 94, 0.15) !important;
        color: #bbf7d0 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 1px solid rgba(34, 197, 94, 0.5) !important;
    }
    
    .stError {
        background: rgba(248, 113, 113, 0.1) !important;
        color: #fecaca !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 1px solid rgba(248, 113, 113, 0.4) !important;
    }
    
    .stWarning {
        background: rgba(250, 204, 21, 0.12) !important;
        color: #facc15 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 1px solid rgba(250, 204, 21, 0.4) !important;
    }
    
    .stInfo {
        background: rgba(15, 98, 254, 0.20) !important;
        color: #e5edff !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 1px solid rgba(129, 140, 248, 0.5) !important;
    }
    
    /* METRICS */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #9ca3af !important;
    }

    /* DATA EDITOR / TABLE */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid rgba(55, 65, 81, 0.9) !important;
        background: #020617 !important;
    }
    
    [data-testid="stDataFrame"] thead tr {
        background: #020617 !important;
    }

    [data-testid="stDataFrame"] thead th {
        background: #020617 !important;
        color: #9ca3af !important;
        font-weight: 500 !important;
        padding: 0.7rem !important;
        border-bottom: 1px solid rgba(55, 65, 81, 0.9) !important;
    }

    [data-testid="stDataFrame"] tbody td {
        background: #020617 !important;
        color: #e5e7eb !important;
        border-bottom: 1px solid rgba(31, 41, 55, 0.9) !important;
    }

    /* TOP-RIGHT TABLE CONTROLS (view buttons etc.) */
    [data-testid="stDataFrame"] button {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border-radius: 8px !important;
        border: 1px solid rgba(55, 65, 81, 0.9) !important;
    }

    [data-testid="stDataFrame"] svg {
        fill: #e5e7eb !important;
        color: #e5e7eb !important;
    }

    /* ---------- SIDEBAR MULTISELECT TAGS (IBM BLUE) ---------- */
    div[data-baseweb="tag"] {
        background: #0f62fe !important;
        color: #ffffff !important;
        border-radius: 999px !important;
        padding: 0.15rem 0.55rem !important;
        border: none !important;
    }
    div[data-baseweb="tag"] span {
        color: #ffffff !important;
    }

    /* ---------- MIN CONFIDENCE SLIDER (GRADIENT TRACK) ---------- */
    /* Label */
    div[data-testid="stSlider"] > label {
        color: #e5e7eb !important;
    }

    /* Slider container */
    div[data-testid="stSlider"] [data-baseweb="slider"] {
        padding-top: 0.4rem !important;
        padding-bottom: 0.2rem !important;
    }

    /* Rail behind track */
    div[data-testid="stSlider"] [data-baseweb="slider"] > div:nth-child(1) {
        background-color: #020617 !important;
        height: 6px !important;
        border-radius: 999px !important;
    }

    /* Gradient active track */
    div[data-testid="stSlider"] [data-baseweb="slider"] > div:nth-child(2) {
        background: linear-gradient(90deg, #8b5cf6 0%, #0f62fe 50%, #22d3ee 100%) !important;
        height: 6px !important;
        border-radius: 999px !important;
    }

    /* Thumb / handle */
    div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #ffffff !important;
        border: 2px solid #0f62fe !important;
        box-shadow: 0 0 0 4px rgba(15, 98, 254, 0.4) !important;
    }

    /* ---------- ACTION INSPECTOR SELECTBOX (DARK) ---------- */

    /* Main select control */
    div[data-baseweb="select"] > div {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border-radius: 10px !important;
        border: 1px solid rgba(55, 65, 81, 0.9) !important;
    }

    div[data-baseweb="select"] span {
        color: #e5e7eb !important;
    }

    /* Popover container */
    div[data-baseweb="popover"] {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border-radius: 10px !important;
        border: 1px solid rgba(55, 65, 81, 0.9) !important;
    }

    /* Menu list in the dropdown */
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] ul {
        background-color: #020617 !important;
        color: #e5e7eb !important;
    }

    /* Individual options */
    div[data-baseweb="menu"] li[role="option"],
    div[data-baseweb="menu"] li[role="option"] * {
        background-color: #020617 !important;
        color: #e5e7eb !important;
    }

    /* Hover / selected option */
    div[data-baseweb="menu"] li[role="option"]:hover,
    div[data-baseweb="menu"] li[role="option"][aria-selected="true"] {
        background-color: #0f62fe !important;
        color: #ffffff !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------- HELPER FUNCTIONS ----------
def format_confidence(conf_raw):
    if conf_raw is None:
        return "N/A"
    if conf_raw <= 1:
        conf_raw *= 100
    return f"{conf_raw:.0f}%"


def status_badge(status):
    status = (status or "staged").lower()
    if status == "executed":
        return "Executed"
    if status == "failed":
        return "Failed"
    return "Staged"


# ---------- SIDEBAR ----------
st.sidebar.title("Decision Board")
st.sidebar.markdown("---")

# Simulate button – safe wrapper
if st.sidebar.button("Simulate Meeting End"):
    try:
        with st.spinner("Processing meeting transcript..."):
            simulate_meeting_end(demo_flag=True)
        st.sidebar.success("Demo meeting processed. Use Refresh to load new actions.")
    except Exception:
        st.sidebar.error("Backend error while processing meeting. Please ask backend owner to check logs.")

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

status_filter = st.sidebar.multiselect(
    "Status",
    options=["staged", "executed", "failed"],
    default=["staged", "executed", "failed"],
)

type_filter = st.sidebar.multiselect(
    "Type",
    options=["email", "jira", "calendar"],
    default=["email", "jira", "calendar"],
)

min_conf = st.sidebar.slider("Minimum Confidence (%)", 0, 100, 0)

st.sidebar.markdown("---")
st.sidebar.subheader("Statistics")

# ---------- MAIN HEADER ----------
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Autonomous Chief of Staff")
    st.caption("Review and approve actions from meeting transcripts")
with col2:
    if st.button("Refresh", use_container_width=True):
        st.rerun()

# ---------- LOAD ACTIONS ----------
with st.spinner("Loading actions..."):
    try:
        actions = get_actions()
        last_loaded = datetime.now()
    except Exception as e:
        st.error(f"Unable to load actions: {e}")
        actions = []
        last_loaded = None

if last_loaded:
    st.caption(f"Last updated: {last_loaded.strftime('%H:%M:%S')}")

# ---------- CALCULATE STATS ----------
total_actions = len(actions)
staged_actions = sum(
    1 for a in actions if (a.get("status") or "staged").lower() == "staged"
)
executed_actions = sum(
    1 for a in actions if (a.get("status") or "").lower() == "executed"
)
failed_actions = sum(
    1 for a in actions if (a.get("status") or "").lower() == "failed"
)

# Sidebar stats
st.sidebar.metric("Total Actions", total_actions)
st.sidebar.metric("Staged", staged_actions)
st.sidebar.metric("Executed", executed_actions)
if failed_actions > 0:
    st.sidebar.metric("Failed", failed_actions)

st.sidebar.markdown("---")
st.sidebar.caption("IBM watsonx.ai & Orchestrate")

# Main stats
st.subheader("Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", total_actions)
c2.metric("Staged", staged_actions)
c3.metric("Executed", executed_actions)
c4.metric("Failed", failed_actions)

st.markdown("---")

# ---------- FILTER ACTIONS ----------
rows = []
for a in actions:
    status = (a.get("status") or "staged").lower()
    if status not in status_filter:
        continue

    action_type = (a.get("type") or "").lower()
    if type_filter and action_type not in type_filter:
        continue

    conf_raw = a.get("confidence")
    pct_val = conf_raw * 100 if conf_raw is not None and conf_raw <= 1 else conf_raw
    if pct_val is not None and pct_val < min_conf:
        continue

    rows.append(
        {
            "id": a.get("id"),
            "Approve": False,
            "Type": action_type.capitalize() if action_type else "N/A",
            "Summary": a.get("summary") or a.get("title") or "No summary",
            "Assignee": a.get("assignee") or "Unassigned",
            "Due Date": a.get("due_date") or "Not set",
            "Confidence": format_confidence(conf_raw),
            "Status": status_badge(status),
            "Snippet": a.get("snippet") or "",
            "_raw_conf": conf_raw,
        }
    )

if not rows:
    st.info("No actions match the current filters.")
    st.stop()

# ---------- TABLE ----------
st.subheader("Actions")

st.info(
    "Edit assignee or due date directly in the table. "
    "Check the Approve box for actions you want to execute."
)

df = pd.DataFrame(rows)

edited_df = st.data_editor(
    df,
    hide_index=True,
    column_config={
        "Approve": st.column_config.CheckboxColumn("Approve", default=False),
        "Type": st.column_config.TextColumn("Type", disabled=True),
        "Summary": st.column_config.TextColumn("Summary", width="large"),
        "Assignee": st.column_config.TextColumn("Assignee"),
        "Due Date": st.column_config.TextColumn("Due Date"),
        "Confidence": st.column_config.TextColumn(
            "Confidence", disabled=True
        ),
        "Status": st.column_config.TextColumn("Status", disabled=True),
        "Snippet": st.column_config.TextColumn("Snippet", disabled=True),
        "id": None,
        "_raw_conf": None,
    },
    disabled=["id", "_raw_conf", "Type", "Confidence", "Status", "Snippet"],
    use_container_width=True,
)

st.markdown("---")

# ---------- ACTION BUTTONS ----------
col1, col2 = st.columns(2)

with col1:
    try:
        selected_count = int(edited_df["Approve"].sum())
    except Exception:
        selected_count = 0

    if st.button(
        f"Approve Selected ({selected_count})",
        type="primary",
        use_container_width=True,
    ):
        try:
            selected_ids = [
                row["id"]
                for _, row in edited_df.iterrows()
                if row.get("Approve", False)
            ]
            if not selected_ids:
                st.warning("No actions selected")
            else:
                with st.spinner(f"Executing {len(selected_ids)} actions..."):
                    errors = []
                    success_count = 0
                    for action_id in selected_ids:
                        try:
                            execute_action(action_id)
                            success_count += 1
                        except Exception as e:
                            errors.append(f"{action_id}: {str(e)}")

                    if errors:
                        st.error(f"{len(errors)} actions failed")
                        for err in errors:
                            st.error(err)
                    if success_count > 0:
                        st.success(
                            f"{success_count} actions executed successfully"
                        )
                    st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    if st.button(
        f"Approve ALL Staged ({staged_actions})", use_container_width=True
    ):
        if staged_actions == 0:
            st.warning("No staged actions")
        else:
            with st.spinner(f"Executing all {staged_actions} actions..."):
                try:
                    execute_all_actions()
                    st.success(f"All {staged_actions} actions executed")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")

# ---------- INSPECTOR ----------
st.subheader("Action Inspector")

if len(edited_df) > 0:
    selected_idx = st.selectbox(
        "Select an action to view details:",
        options=list(range(len(edited_df))),
        format_func=lambda i: f"{edited_df.iloc[i]['Type']} - {edited_df.iloc[i]['Summary'][:50]}",
    )

    row = edited_df.iloc[selected_idx]

    st.markdown(
        f"""
    <div style='background: #020617; padding: 1.5rem; border-radius: 14px;
                border: 1px solid rgba(15, 98, 254, 0.5); box-shadow: 0 10px 30px rgba(0,0,0,0.6);'>
        <h4 style='color: #ffffff; margin-top: 0; margin-bottom: 0.8rem; font-weight: 600;'>
            Details
        </h4>
        <p><strong>Type:</strong> {row['Type']}</p>
        <p><strong>Summary:</strong> {row['Summary']}</p>
        <p><strong>Assignee:</strong> {row['Assignee']}</p>
        <p><strong>Due Date:</strong> {row['Due Date']}</p>
        <p><strong>Confidence:</strong> {row['Confidence']}</p>
        <p><strong>Status:</strong> {row['Status']}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("**Transcript Snippet:**")
    if row["Snippet"]:
        st.info(row["Snippet"])
    else:
        st.warning("No transcript snippet available")
else:
    st.info("No actions to inspect")

st.markdown("---")
st.caption("Built with IBM watsonx.ai and watsonx Orchestrate")
