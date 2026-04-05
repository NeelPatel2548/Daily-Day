"""
daily_runner.py — runs from repo root via GitHub Actions
Natural randomness: commit count varies 2-7 per day, no fixed pattern.
"""

import sys
import os
import random
import hashlib
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from dsa_problems import pick_problem
from quote_fetcher import fetch_quote

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST)
DATE_SLUG = TODAY.strftime("%Y-%m-%d")
DATE_HUMAN = TODAY.strftime("%d %b %Y")
WEEKDAY = TODAY.strftime("%A")
DAY_OF_WEEK = TODAY.weekday()  # 0=Monday, 6=Sunday

DSA_DIR = "dsa"
QUOTE_FILE = "quotes/QUOTES_LOG.md"
STATE_FILE = ".github/daily_state.txt"


def day_seed():
    """Unique seed per day — same phase always gets same skip decision today."""
    return int(hashlib.md5(DATE_SLUG.encode()).hexdigest(), 16)


def should_run(phase: str) -> bool:
    """
    Decide whether a phase runs today using a day-based seed so all
    5 workflow triggers agree on the same decision for a given phase.

    Natural distribution:
    - Weekdays:  avg 3-4 commits  (developer busy with work)
    - Weekends:  avg 5-6 commits  (more free time to grind)
    - Rare lazy days: just 2 commits (happens ~10% of days)
    """
    rng = random.Random(day_seed() + int(phase))
    roll = rng.random()

    is_weekend = DAY_OF_WEEK >= 5  # Saturday or Sunday
    lazy_day = random.Random(day_seed()).random() < 0.10  # 10% chance of lazy day

    if lazy_day:
        # Lazy day — only phases 1, 2, 3 guaranteed (2-3 commits max)
        return phase in ("1", "2", "3")

    if is_weekend:
        # Weekend — more active
        thresholds = {
            "1": 1.0,   # always
            "2": 1.0,   # always
            "3": 1.0,   # always
            "4": 0.90,  # 90%
            "5": 0.80,  # 80%
            "6": 0.65,  # 65%
            "7": 0.45,  # 45%
        }
    else:
        # Weekday — more conservative
        thresholds = {
            "1": 1.0,   # always
            "2": 1.0,   # always
            "3": 1.0,   # always
            "4": 0.75,  # 75%
            "5": 0.55,  # 55%
            "6": 0.35,  # 35%
            "7": 0.20,  # 20%
        }

    return roll < thresholds.get(phase, 0.5)


def read_state():
    if not os.path.exists(STATE_FILE):
        return {}
    data = {}
    with open(STATE_FILE) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                data[k] = v
    return data


def write_state(data):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")


def dsa_filepath(slug):
    return os.path.join(DSA_DIR, DATE_SLUG, f"{slug}.py")


def phase_1_create_dsa():
    problem = pick_problem(DATE_SLUG)
    slug = problem["slug"]
    path = dsa_filepath(slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    content = f'''# {problem["title"]}
# Difficulty: {problem["difficulty"]} | Topic: {problem["topic"]}
# Date: {DATE_HUMAN}
#
# Problem:
# {chr(10).join("# " + line for line in problem["description"].splitlines())}
#
# Examples:
# {chr(10).join("# " + ex for ex in problem["examples"])}

# TODO: think through approach

def {problem["fn_name"]}({problem["params"]}):
    pass
'''
    with open(path, "w") as f:
        f.write(content)

    write_state({"slug": slug, "date": DATE_SLUG, "phase": "1"})
    print(f"[phase 1] created {path}")


def phase_2_add_approach():
    state = read_state()
    slug = state.get("slug", "")
    path = dsa_filepath(slug)
    if not os.path.exists(path):
        print("[phase 2] file not found, skipping")
        return

    problem = pick_problem(DATE_SLUG)

    with open(path) as f:
        src = f.read()

    approach_block = f'''
# Approach:
# {problem["approach"]}
#
# Time complexity: {problem["time_complexity"]}
# Space complexity: {problem["space_complexity"]}

'''
    src = src.replace("# TODO: think through approach\n", approach_block, 1)

    with open(path, "w") as f:
        f.write(src)

    write_state({**state, "phase": "2"})
    print(f"[phase 2] added approach to {path}")


def phase_3_add_solution():
    state = read_state()
    slug = state.get("slug", "")
    path = dsa_filepath(slug)
    if not os.path.exists(path):
        print("[phase 3] file not found, skipping")
        return

    problem = pick_problem(DATE_SLUG)

    with open(path) as f:
        src = f.read()

    src = src.replace("    pass\n", problem["solution"] + "\n", 1)

    with open(path, "w") as f:
        f.write(src)

    write_state({**state, "phase": "3"})
    print(f"[phase 3] added solution to {path}")


def phase_4_quote():
    if not should_run("4"):
        print("[phase 4] skipping today")
        return

    os.makedirs("quotes", exist_ok=True)
    quote, author = fetch_quote()

    if not os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "w") as f:
            f.write("# Daily Quotes\n\nOne quote, every day.\n\n---\n")

    with open(QUOTE_FILE, "a") as f:
        f.write(f"\n### {WEEKDAY}, {DATE_HUMAN}\n> \"{quote}\"\n>\n> — *{author}*\n")

    print(f"[phase 4] appended quote by {author}")


def phase_5_cleanup():
    if not should_run("5"):
        print("[phase 5] skipping today")
        return

    state = read_state()
    slug = state.get("slug", "")
    path = dsa_filepath(slug)
    if not os.path.exists(path):
        print("[phase 5] file not found, skipping")
        return

    problem = pick_problem(DATE_SLUG)
    tests = "\n\n# --- quick tests ---\n"
    for tc in problem.get("test_cases", []):
        tests += f"# {tc}\n"
    tests += f"# solved on {DATE_HUMAN}\n"

    with open(path, "a") as f:
        f.write(tests)

    write_state({**state, "phase": "5"})
    print(f"[phase 5] added test cases to {path}")


def phase_6_refactor():
    if not should_run("6"):
        print("[phase 6] skipping today")
        return

    state = read_state()
    slug = state.get("slug", "")
    path = dsa_filepath(slug)
    if not os.path.exists(path):
        print("[phase 6] file not found, skipping")
        return

    note = f"\n# Refactor note: reviewed on {DATE_HUMAN} — solution looks clean.\n"

    with open(path, "a") as f:
        f.write(note)

    write_state({**state, "phase": "6"})
    print(f"[phase 6] added refactor note to {path}")


def phase_7_optimize():
    if not should_run("7"):
        print("[phase 7] skipping today")
        return

    state = read_state()
    slug = state.get("slug", "")
    path = dsa_filepath(slug)
    if not os.path.exists(path):
        print("[phase 7] file not found, skipping")
        return

    problem = pick_problem(DATE_SLUG)
    note = f"\n# Alternative: {problem['approach'].splitlines()[0]}\n"
    note += f"# Could optimize further depending on input constraints.\n"

    with open(path, "a") as f:
        f.write(note)

    write_state({**state, "phase": "7"})
    print(f"[phase 7] added optimization note to {path}")


PHASES = {
    "1": phase_1_create_dsa,
    "2": phase_2_add_approach,
    "3": phase_3_add_solution,
    "4": phase_4_quote,
    "5": phase_5_cleanup,
    "6": phase_6_refactor,
    "7": phase_7_optimize,
}

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "1"
    handler = PHASES.get(phase)
    if handler:
        handler()
    else:
        print(f"Unknown phase: {phase}")
        sys.exit(1)
