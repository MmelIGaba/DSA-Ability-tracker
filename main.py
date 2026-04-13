# main.py
# Controller — now routes through dashboard

import json
import os
from datetime import datetime, date
from roadmap import ROADMAP
from ai_engine import generate_next_step, get_next_uncompleted
from dashboard import render_dashboard

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
PROGRESS_FILE = "progress.json"


# ─────────────────────────────────────────────
# FILE OPERATIONS
# ─────────────────────────────────────────────
def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        default = {
            "completed":         [],
            "in_progress":       [],
            "current_focus":     None,
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
# STREAK LOGIC
# ─────────────────────────────────────────────
def update_streak(progress):
    today     = str(date.today())
    last_date = progress.get("last_session_date")

    if last_date is None:
        progress["streak_days"]       = 1
        progress["last_session_date"] = today

    elif last_date == today:
        pass  # Same day, no change

    elif (date.today() - date.fromisoformat(last_date)).days == 1:
        # Consecutive day
        progress["streak_days"]       += 1
        progress["last_session_date"] = today

    else:
        # Streak broken
        progress["streak_days"]       = 1
        progress["last_session_date"] = today

    return progress


# ─────────────────────────────────────────────
# ACTIONS
# ─────────────────────────────────────────────
def action_mark_done(progress):
    print("\n── Mark Problem as Complete ──")
    print("Enter problem ID (or 'q' to cancel):")
    user_input = input(">>> ").strip()

    if user_input.lower() == 'q':
        return progress

    if not user_input.isdigit():
        print("❌ Invalid — enter a number.")
        input("Press Enter to continue...")
        return progress

    pid = int(user_input)

    if pid not in ROADMAP:
        print(f"❌ Problem {pid} not in roadmap.")
        input("Press Enter to continue...")
        return progress

    if pid in progress["completed"]:
        print(f"⚠️  Already completed.")
        input("Press Enter to continue...")
        return progress

    # Move from in_progress if it was there
    if pid in progress["in_progress"]:
        progress["in_progress"].remove(pid)

    progress["completed"].append(pid)
    progress["completed"].sort()
    progress["last_completed_id"] = pid

    print(f"✅ Done: [{pid}] {ROADMAP[pid]}")
    save_progress(progress)
    input("Press Enter to continue...")
    return progress


def action_move_to_in_progress(progress):
    print("\n── Move Problem to In Progress ──")

    if len(progress["in_progress"]) >= 3:
        print("⚠️  In Progress column is full (max 3).")
        print("    Complete or remove one first.")
        input("Press Enter to continue...")
        return progress

    print("Enter problem ID (or 'q' to cancel):")
    user_input = input(">>> ").strip()

    if user_input.lower() == 'q':
        return progress

    if not user_input.isdigit():
        print("❌ Invalid — enter a number.")
        input("Press Enter to continue...")
        return progress

    pid = int(user_input)

    if pid not in ROADMAP:
        print(f"❌ Problem {pid} not in roadmap.")
        input("Press Enter to continue...")
        return progress

    if pid in progress["completed"]:
        print("⚠️  Already completed — can't move to In Progress.")
        input("Press Enter to continue...")
        return progress

    if pid in progress["in_progress"]:
        print("⚠️  Already in In Progress.")
        input("Press Enter to continue...")
        return progress

    progress["in_progress"].append(pid)
    print(f"🔥 Moved to In Progress: [{pid}] {ROADMAP[pid]}")
    save_progress(progress)
    input("Press Enter to continue...")
    return progress


def action_get_ai_plan(progress):
    print("\n" + "═" * 66)
    print("              🤖 AI COACH — NEXT STEPS")
    print("═" * 66)
    prompt = generate_next_step(progress["completed"], ROADMAP)
    print(prompt)
    print("═" * 66)
    print("💡 Paste this into ChatGPT or connect OpenAI in ai_engine.py")
    input("\nPress Enter to return to dashboard...")


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
def main():
    progress = load_progress()
    progress["session_count"] += 1
    progress = update_streak(progress)
    save_progress(progress)

    while True:
        render_dashboard(progress)
        choice = input(">>> ").strip()

        if choice == "1":
            action_get_ai_plan(progress)

        elif choice == "2":
            progress = action_mark_done(progress)

        elif choice == "3":
            progress = action_move_to_in_progress(progress)

        elif choice == "4":
            print("\n👋 See you next session. Keep going.\n")
            break

        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()