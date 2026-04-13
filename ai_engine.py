# ai_engine.py
# Responsible for ONE thing: generating the AI prompt
# Plug OpenAI API in here when ready — today just prints the prompt

import os
from roadmap import TIERS

# ─────────────────────────────────────────────
# HELPER: Figure out which tier each problem belongs to
# ─────────────────────────────────────────────
def get_tier_for_problem(problem_id):
    for tier_name, tier_range in TIERS.items():
        if problem_id in tier_range:
            return tier_name
    return "Unknown"


# ─────────────────────────────────────────────
# HELPER: Analyze weak areas from completed list
# ─────────────────────────────────────────────
def analyze_weak_areas(completed_ids, roadmap):
    tier_completion = {}

    for tier_name, tier_range in TIERS.items():
        total     = len(tier_range)
        done      = sum(1 for i in tier_range if i in completed_ids)
        pct       = round((done / total) * 100)
        tier_completion[tier_name] = {
            "done":    done,
            "total":   total,
            "percent": pct
        }

    return tier_completion


# ─────────────────────────────────────────────
# HELPER: Find next uncompleted problems
# ─────────────────────────────────────────────
def get_next_uncompleted(completed_ids, roadmap, count=3):
    next_problems = []
    for pid, pname in roadmap.items():
        if pid not in completed_ids:
            next_problems.append((pid, pname))
        if len(next_problems) == count:
            break
    return next_problems


# ─────────────────────────────────────────────
# CORE FUNCTION: Build the AI prompt
# ─────────────────────────────────────────────
def generate_next_step(completed_ids, roadmap):
    
    # Build readable completed list
    completed_str = "\n".join(
        f"  [{pid}] {roadmap[pid]} ({get_tier_for_problem(pid)})"
        for pid in completed_ids
        if pid in roadmap
    ) or "  None yet — just getting started."

    # Build full roadmap string
    roadmap_str = "\n".join(
        f"  [{pid}] {pname}"
        for pid, pname in roadmap.items()
    )

    # Tier breakdown
    tier_analysis = analyze_weak_areas(completed_ids, roadmap)
    tier_str = "\n".join(
        f"  {tier}: {data['done']}/{data['total']} ({data['percent']}%)"
        for tier, data in tier_analysis.items()
    )

    # Next 3 uncompleted problems (for AI context)
    next_up = get_next_uncompleted(completed_ids, roadmap, count=5)
    next_str = "\n".join(
        f"  [{pid}] {pname}"
        for pid, pname in next_up
    )

    # ── THE PROMPT ──────────────────────────────────────────
    prompt = f"""
You are an expert DSA coach helping a developer prepare for technical interviews.

════════════════════════════════════════
STUDENT PROGRESS REPORT
════════════════════════════════════════

✅ Completed Problems:
{completed_str}

📊 Tier Completion Breakdown:
{tier_str}

📚 Next 5 Available Problems:
{next_str}

════════════════════════════════════════
FULL ROADMAP (50 patterns):
════════════════════════════════════════
{roadmap_str}

════════════════════════════════════════
YOUR TASK:
════════════════════════════════════════
1. Identify the student's WEAKEST area based on tier completion
2. Recommend the NEXT 3 problems they should solve TODAY
3. For each problem, briefly explain:
   - Why this problem matters
   - What pattern/concept it teaches
   - Estimated time to solve (for a beginner)
4. Give ONE motivational insight about their current progress

Format your response clearly with headers.
Keep it practical, not generic.
"""
    return prompt


# ─────────────────────────────────────────────
# OPTIONAL: OpenAI call (uncomment when ready)
# ─────────────────────────────────────────────
def call_openai(prompt):
    """
    Uncomment this when you have your API key ready.
    pip install openai
    """
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert DSA coach."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content
    pass
