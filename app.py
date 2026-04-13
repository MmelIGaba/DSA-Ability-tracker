# app.py
# Streamlit Kanban Dashboard for DSA Ability Tracker

import json
import os
import streamlit as st
from datetime import datetime, date
from roadmap import ROADMAP, TIERS
from ai_engine import generate_next_step

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title  = "DSA Ability Tracker",
    page_icon   = "🧠",
    layout      = "wide",
    initial_sidebar_state = "collapsed"
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── General ── */
body { background-color: #0e1117; }

/* ── Kanban Cards ── */
.card {
    background-color: #1e2130;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 4px solid #555;
    font-size: 13px;
    line-height: 1.6;
}
.card-backlog   { border-left-color: #4a9eff; }
.card-progress  { border-left-color: #ff7043; }
.card-done      { border-left-color: #66bb6a; }

.card-title {
    font-weight: 700;
    font-size: 14px;
    color: #e0e0e0;
}
.card-meta {
    color: #9e9e9e;
    font-size: 12px;
}

/* ── Column Headers ── */
.col-header {
    text-align: center;
    font-size: 16px;
    font-weight: 800;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 14px;
    letter-spacing: 0.5px;
}
.col-backlog  { background-color: #1a2744; color: #4a9eff; }
.col-progress { background-color: #2d1f1a; color: #ff7043; }
.col-done     { background-color: #1a2d1f; color: #66bb6a; }

/* ── Tier Health Bar ── */
.tier-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    font-size: 13px;
}
.tier-label {
    width: 200px;
    color: #ccc;
}
.tier-bar-bg {
    background-color: #2a2a2a;
    border-radius: 6px;
    height: 12px;
    width: 200px;
    overflow: hidden;
    margin: 0 12px;
}
.tier-bar-fill {
    height: 12px;
    border-radius: 6px;
    background: linear-gradient(90deg, #4a9eff, #66bb6a);
}
.tier-stats {
    color: #888;
    font-size: 12px;
    width: 100px;
}

/* ── Stat Cards ── */
.stat-box {
    background-color: #1e2130;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-value {
    font-size: 32px;
    font-weight: 800;
    color: #4a9eff;
}
.stat-label {
    font-size: 12px;
    color: #888;
    margin-top: 4px;
}

/* ── AI Box ── */
.ai-box {
    background-color: #1a1f2e;
    border: 1px solid #2a3555;
    border-radius: 10px;
    padding: 20px;
    font-size: 13px;
    line-height: 1.8;
    color: #ccc;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────
PROGRESS_FILE = "progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        default = {
            "completed":         [],
            "in_progress":       [],
            "session_count":     0,
            "last_updated":      None,
            "last_completed_id": None,
            "streak_days":       0,
            "last_session_date": None
        }
        save_progress(default)
        return default
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(data):
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
TIME_ESTIMATES = {
    "Array Basics":         "20 min",
    "Sorting & Searching":  "40 min",
    "Two Pointers/Sliding": "45 min",
    "Hashing":              "35 min",
    "Linked Lists":         "40 min",
    "Stacks & Queues":      "45 min",
    "Intervals & Greedy":   "50 min",
}

def get_tier(pid):
    for tier_name, tier_range in TIERS.items():
        if pid in tier_range:
            return tier_name
    return "Unknown"

def get_time(pid):
    return TIME_ESTIMATES.get(get_tier(pid), "30 min")

def update_streak(progress):
    today     = str(date.today())
    last_date = progress.get("last_session_date")
    if last_date is None:
        progress["streak_days"]       = 1
        progress["last_session_date"] = today
    elif last_date == today:
        pass
    elif (date.today() - date.fromisoformat(last_date)).days == 1:
        progress["streak_days"]       += 1
        progress["last_session_date"] = today
    else:
        progress["streak_days"]       = 1
        progress["last_session_date"] = today
    return progress

def make_card_html(pid, card_type="backlog"):
    name  = ROADMAP[pid]
    tier  = get_tier(pid)
    time  = get_time(pid)

    icons = {
        "backlog":  ("📋", "card-backlog"),
        "progress": ("🔥", "card-progress"),
        "done":     ("✅", "card-done"),
    }
    icon, css_class = icons.get(card_type, ("📋", "card-backlog"))

    return f"""
    <div class="card {css_class}">
        <div class="card-title">{icon} [{pid:02d}] {name}</div>
        <div class="card-meta">📂 {tier} &nbsp;|&nbsp; ⏱ {time}</div>
    </div>
    """


# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
if "progress" not in st.session_state:
    p = load_progress()
    p["session_count"] += 1
    p = update_streak(p)
    save_progress(p)
    st.session_state.progress = p


# ─────────────────────────────────────────────
# SECTION 1 — HEADER
# ─────────────────────────────────────────────
progress = st.session_state.progress
total    = len(ROADMAP)
done     = len(progress["completed"])
pct      = round((done / total) * 100)
streak   = progress.get("streak_days", 0)
last_id  = progress.get("last_completed_id")
last_name = ROADMAP.get(last_id, "—") if last_id else "—"

st.markdown("## 🧠 DSA Ability Tracker")
st.caption(f"Session #{progress['session_count']}  ·  Last updated: {progress['last_updated'] or 'Never'}")

# ── Stat Boxes ────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">{done}/{total}</div>
        <div class="stat-label">Problems Done</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">{pct}%</div>
        <div class="stat-label">Overall Progress</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">🔥 {streak}</div>
        <div class="stat-label">Day Streak</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-value">{len(progress.get('in_progress', []))}/3</div>
        <div class="stat-label">In Progress</div>
    </div>""", unsafe_allow_html=True)

# ── Progress Bar ──────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.progress(pct / 100, text=f"Overall Roadmap — {pct}% complete")
st.markdown("---")


# ─────────────────────────────────────────────
# SECTION 2 — KANBAN BOARD
# ─────────────────────────────────────────────
completed_ids   = progress["completed"]
in_progress_ids = progress.get("in_progress", [])

backlog_all     = [
    pid for pid in ROADMAP
    if pid not in completed_ids
    and pid not in in_progress_ids
]
backlog_preview = backlog_all[:5]
backlog_extra   = len(backlog_all) - 5

st.markdown("### 🗂️ Kanban Board")

col_b, col_p, col_d = st.columns(3)

# ── BACKLOG COLUMN ────────────────────────────
with col_b:
    st.markdown(
        f'<div class="col-header col-backlog">📋 BACKLOG ({len(backlog_all)})</div>',
        unsafe_allow_html=True
    )
    if backlog_preview:
        for pid in backlog_preview:
            st.markdown(make_card_html(pid, "backlog"), unsafe_allow_html=True)
        if backlog_extra > 0:
            st.caption(f"+ {backlog_extra} more problems remaining")
    else:
        st.success("Backlog clear! 🎉")

# ── IN PROGRESS COLUMN ────────────────────────
with col_p:
    st.markdown(
        f'<div class="col-header col-progress">🔥 IN PROGRESS ({len(in_progress_ids)}/3)</div>',
        unsafe_allow_html=True
    )
    if in_progress_ids:
        for pid in in_progress_ids[:3]:
            st.markdown(make_card_html(pid, "progress"), unsafe_allow_html=True)
    else:
        st.info("Nothing in progress yet.\nPick a problem below ↓")

# ── DONE COLUMN ───────────────────────────────
with col_d:
    st.markdown(
        f'<div class="col-header col-done">✅ DONE ({len(completed_ids)})</div>',
        unsafe_allow_html=True
    )
    if completed_ids:
        for pid in reversed(completed_ids[-6:]):
            st.markdown(make_card_html(pid, "done"), unsafe_allow_html=True)
    else:
        st.warning("Nothing completed yet.\nLet's go! 💪")

st.markdown("---")


# ─────────────────────────────────────────────
# SECTION 3 — TIER HEALTH
# ─────────────────────────────────────────────
st.markdown("### 📊 Tier Health")

tier_cols = st.columns(2)

for i, (tier_name, tier_range) in enumerate(TIERS.items()):
    t_total = len(tier_range)
    t_done  = sum(1 for pid in tier_range if pid in completed_ids)
    t_pct   = round((t_done / t_total) * 100)

    icon = "✅" if t_pct == 100 else ("⚠️" if t_pct >= 50 else "❌")

    with tier_cols[i % 2]:
        st.markdown(f"**{icon} {tier_name}**  —  {t_done}/{t_total} ({t_pct}%)")
        st.progress(t_pct / 100)

st.markdown("---")


# ─────────────────────────────────────────────
# SECTION 4 — ACTIONS
# ─────────────────────────────────────────────
st.markdown("### ⚡ Actions")

action_col1, action_col2 = st.columns(2)

# ── Mark Done ─────────────────────────────────
with action_col1:
    st.markdown("#### ✅ Mark Problem as Done")

    available_to_complete = {
        pid: f"[{pid:02d}] {ROADMAP[pid]}"
        for pid in ROADMAP
        if pid not in completed_ids
    }

    if available_to_complete:
        selected_done = st.selectbox(
            "Select a problem to mark complete:",
            options  = list(available_to_complete.keys()),
            format_func = lambda x: available_to_complete[x],
            key      = "select_done"
        )
        if st.button("✅ Mark as Done", use_container_width=True):
            if selected_done in in_progress_ids:
                progress["in_progress"].remove(selected_done)
            progress["completed"].append(selected_done)
            progress["completed"].sort()
            progress["last_completed_id"] = selected_done
            save_progress(progress)
            st.session_state.progress = progress
            st.success(f"✅ Completed: [{selected_done}] {ROADMAP[selected_done]}")
            st.rerun()
    else:
        st.success("🎉 All problems completed!")


# ── Move to In Progress ────────────────────────
with action_col2:
    st.markdown("#### 🔥 Move to In Progress")

    available_to_start = {
        pid: f"[{pid:02d}] {ROADMAP[pid]}"
        for pid in ROADMAP
        if pid not in completed_ids
        and pid not in in_progress_ids
    }

    if len(in_progress_ids) >= 3:
        st.warning("⚠️ In Progress is full (max 3). Complete one first.")

    elif available_to_start:
        selected_prog = st.selectbox(
            "Select a problem to start:",
            options     = list(available_to_start.keys()),
            format_func = lambda x: available_to_start[x],
            key         = "select_progress"
        )
        if st.button("🔥 Move to In Progress", use_container_width=True):
            progress["in_progress"].append(selected_prog)
            save_progress(progress)
            st.session_state.progress = progress
            st.success(f"🔥 Started: [{selected_prog}] {ROADMAP[selected_prog]}")
            st.rerun()

st.markdown("---")


# ─────────────────────────────────────────────
# SECTION 5 — AI COACH
# ─────────────────────────────────────────────
st.markdown("### 🤖 AI Coach")

if st.button("🧠 Generate My Next Study Plan", use_container_width=True):
    with st.spinner("Generating your personalized plan..."):
        prompt = generate_next_step(progress["completed"], ROADMAP)
        st.markdown("#### 📋 AI Prompt (paste into ChatGPT or connect API)")
        st.markdown(
            f'<div class="ai-box">{prompt}</div>',
            unsafe_allow_html=True
        )
        st.caption("💡 To automate this: add your OpenAI API key to ai_engine.py")
