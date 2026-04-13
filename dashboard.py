# dashboard.py
# Renders the full Kanban-style CLI dashboard
# Completely separate from logic — only responsible for display

from datetime import datetime
from roadmap import ROADMAP, TIERS

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
BOARD_WIDTH     = 66      # total terminal width
COL_WIDTH       = 20      # each kanban column width
BACKLOG_PREVIEW = 5       # how many backlog items to show

# Time estimates per tier (minutes)
TIME_ESTIMATES = {
    "Array Basics":         "20 min",
    "Sorting & Searching":  "40 min",
    "Two Pointers/Sliding": "45 min",
    "Hashing":              "35 min",
    "Linked Lists":         "40 min",
    "Stacks & Queues":      "45 min",
    "Intervals & Greedy":   "50 min",
}

# Status icons per tier health
HEALTH_ICON = {
    100: "✅",
    0:   "❌",
}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_tier(problem_id):
    for tier_name, tier_range in TIERS.items():
        if problem_id in tier_range:
            return tier_name
    return "Unknown"


def get_time_estimate(problem_id):
    tier = get_tier(problem_id)
    return TIME_ESTIMATES.get(tier, "30 min")


def get_health_icon(percent):
    if percent == 100:
        return "✅"
    elif percent >= 50:
        return "⚠️ "
    else:
        return "❌"


def make_progress_bar(done, total, bar_length=20):
    filled = int((done / total) * bar_length) if total > 0 else 0
    bar    = "█" * filled + "░" * (bar_length - filled)
    return bar


def truncate(text, max_len):
    """Truncate text with ellipsis if too long"""
    return text if len(text) <= max_len else text[:max_len - 2] + ".."


def divider(char="═", width=BOARD_WIDTH):
    print(char * width)


# ─────────────────────────────────────────────
# SECTION 1 — HEADER STATS BAR
# ─────────────────────────────────────────────
def render_header(progress):
    total     = len(ROADMAP)
    done      = len(progress["completed"])
    pct       = round((done / total) * 100)
    bar       = make_progress_bar(done, total)
    session   = progress["session_count"]
    streak    = progress.get("streak_days", 0)
    last_id   = progress.get("last_completed_id")
    last_name = ROADMAP.get(last_id, "Nothing yet") if last_id else "Nothing yet"
    last_name = truncate(last_name, 22)

    divider()
    print(f"  🧠  DSA ABILITY TRACKER{' ' * 27}Session #{session}")
    divider()
    print(f"  Progress : {bar}  {done}/{total} ({pct}%)")
    print(f"  Streak   : 🔥 {streak} day(s)  |  Last Done : [{last_id or '--'}] {last_name}")
    divider()


# ─────────────────────────────────────────────
# SECTION 2 — KANBAN BOARD
# ─────────────────────────────────────────────
def render_kanban(progress):
    completed_ids   = progress["completed"]
    in_progress_ids = progress.get("in_progress", [])

    # ── Build column data ──────────────────────────────────
    # BACKLOG: not completed, not in progress
    backlog_all = [
        pid for pid in ROADMAP
        if pid not in completed_ids
        and pid not in in_progress_ids
    ]
    backlog_preview = backlog_all[:BACKLOG_PREVIEW]
    backlog_extra   = len(backlog_all) - BACKLOG_PREVIEW

    # IN PROGRESS: from progress.json (max 3)
    in_prog = in_progress_ids[:3]

    # DONE: completed list (show last 6 to keep board balanced)
    done_preview = completed_ids[-6:] if completed_ids else []

    # ── Column headers ─────────────────────────────────────
    backlog_header  = f"  📋 BACKLOG ({len(backlog_all)})"
    inprog_header   = f"  🔥 IN PROGRESS ({len(in_prog)}/3)"
    done_header     = f"  ✅ DONE ({len(completed_ids)})"

    print(f"\n{'─' * BOARD_WIDTH}")
    print(
        f"{'─':<1}"
        f"{backlog_header:<22}"
        f"{'│':<1}"
        f"{inprog_header:<22}"
        f"{'│':<1}"
        f"{done_header:<22}"
        f"{'─':>1}"
    )
    print(f"{'─' * BOARD_WIDTH}")

    # ── Build card lines ───────────────────────────────────
    def make_card(pid):
        name  = truncate(ROADMAP[pid], 16)
        tier  = truncate(get_tier(pid), 14)
        time  = get_time_estimate(pid)
        line1 = f" [{pid:02d}] {name}"
        line2 = f"  ╰ {tier} | {time}"
        return line1, line2

    # Pad columns to same height so the board looks even
    def pad_column(items, empty_label="  (empty)"):
        if not items:
            return [(empty_label, "")]
        return [make_card(pid) for pid in items]

    backlog_cards  = pad_column(backlog_preview)
    inprog_cards   = pad_column(in_prog)
    done_cards     = pad_column(done_preview)

    max_rows = max(len(backlog_cards), len(inprog_cards), len(done_cards))

    # ── Render rows ────────────────────────────────────────
    for i in range(max_rows):
        # Line 1 of card (name)
        b1 = backlog_cards[i][0]  if i < len(backlog_cards)  else ""
        p1 = inprog_cards[i][0]   if i < len(inprog_cards)   else ""
        d1 = done_cards[i][0]     if i < len(done_cards)      else ""

        print(
            f"│ {b1:<20}│ {p1:<20}│ {d1:<20}│"
        )

        # Line 2 of card (tier + time)
        b2 = backlog_cards[i][1]  if i < len(backlog_cards)  else ""
        p2 = inprog_cards[i][1]   if i < len(inprog_cards)   else ""
        d2 = done_cards[i][1]     if i < len(done_cards)      else ""

        print(
            f"│ {b2:<20}│ {p2:<20}│ {d2:<20}│"
        )

        # Spacing between cards
        print(f"│ {'─' * 20}│ {'─' * 20}│ {'─' * 20}│")

    # Show backlog overflow count
    if backlog_extra > 0:
        msg = f"  + {backlog_extra} more in backlog"
        print(f"│ {msg:<20}│ {'':20}│ {'':20}│")

    print(f"{'─' * BOARD_WIDTH}\n")


# ─────────────────────────────────────────────
# SECTION 3 — TIER HEALTH BAR
# ─────────────────────────────────────────────
def render_tier_health(progress):
    completed_ids = progress["completed"]

    print("  TIER HEALTH:")
    print(f"  {'─' * 60}")

    for tier_name, tier_range in TIERS.items():
        total   = len(tier_range)
        done    = sum(1 for i in tier_range if i in completed_ids)
        pct     = round((done / total) * 100)
        bar     = make_progress_bar(done, total, bar_length=16)
        icon    = get_health_icon(pct)
        label   = truncate(tier_name, 22)

        print(f"  {label:<22}  {bar}  {done:>2}/{total:<2}  {pct:>3}%  {icon}")

    print(f"  {'─' * 60}\n")


# ─────────────────────────────────────────────
# SECTION 4 — ACTION MENU
# ─────────────────────────────────────────────
def render_menu():
    divider()
    print(
        "  [1] Get AI Plan   "
        "[2] Mark Done   "
        "[3] Move to In Progress   "
        "[4] Exit"
    )
    divider()


# ─────────────────────────────────────────────
# MASTER RENDER — Call this one function
# ─────────────────────────────────────────────
def render_dashboard(progress):
    # Clear screen for clean refresh
    print("\033[H\033[J", end="")

    render_header(progress)
    print()
    render_kanban(progress)
    render_tier_health(progress)
    render_menu()

