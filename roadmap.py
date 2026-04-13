# roadmap.py
# Your 50 DSA patterns — this is your master syllabus
# Organized by difficulty tier so AI can track progression

ROADMAP = {
    # ── TIER 1: Array Basics (1–10) ──────────────────────────
    1:  "Reverse an array",
    2:  "Find max and min in array",
    3:  "Find second largest element",
    4:  "Check if array is sorted",
    5:  "Remove duplicates from sorted array",
    6:  "Left rotate array by one",
    7:  "Move zeros to end",
    8:  "Linear search",
    9:  "Union and intersection of two arrays",
    10: "Missing number in array",

    # ── TIER 2: Sorting & Searching (11–20) ──────────────────
    11: "Bubble sort",
    12: "Selection sort",
    13: "Insertion sort",
    14: "Merge sort",
    15: "Quick sort",
    16: "Binary search",
    17: "Search in rotated sorted array",
    18: "Find first and last position of element",
    19: "Count occurrences in sorted array",
    20: "Square root using binary search",

    # ── TIER 3: Two Pointers & Sliding Window (21–28) ────────
    21: "Two sum (sorted array)",
    22: "Three sum",
    23: "Container with most water",
    24: "Trapping rainwater",
    25: "Maximum subarray (Kadane's algorithm)",
    26: "Longest substring without repeating characters",
    27: "Maximum sum subarray of size K",
    28: "Smallest window containing substring",

    # ── TIER 4: Hashing (29–33) ──────────────────────────────
    29: "Two sum (unsorted, using hashmap)",
    30: "Group anagrams",
    31: "Longest consecutive sequence",
    32: "Subarray sum equals K",
    33: "Top K frequent elements",

    # ── TIER 5: Linked Lists (34–39) ─────────────────────────
    34: "Reverse a linked list",
    35: "Detect cycle in linked list",
    36: "Find middle of linked list",
    37: "Merge two sorted linked lists",
    38: "Remove Nth node from end",
    39: "Intersection of two linked lists",

    # ── TIER 6: Stacks & Queues (40–44) ──────────────────────
    40: "Valid parentheses",
    41: "Min stack",
    42: "Next greater element",
    43: "Implement queue using stacks",
    44: "Largest rectangle in histogram",

    # ── TIER 7: Intervals & Greedy (45–50) ───────────────────
    45: "Meeting rooms (can attend all?)",
    46: "Merge intervals",
    47: "Insert interval",
    48: "Non-overlapping intervals",
    49: "Jump game",
    50: "Activity selection problem",
}

# Tier labels — used by AI engine for context
TIERS = {
    "Array Basics":          range(1, 11),
    "Sorting & Searching":   range(11, 21),
    "Two Pointers/Sliding":  range(21, 29),
    "Hashing":               range(29, 34),
    "Linked Lists":          range(34, 40),
    "Stacks & Queues":       range(40, 45),
    "Intervals & Greedy":    range(45, 51),
}
