"""
daily_runner.py — runs from repo root via GitHub Actions
"""

import sys
import os
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from dsa_problems import pick_problem
from quote_fetcher import fetch_quote

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST)
DATE_SLUG = TODAY.strftime("%Y-%m-%d")
DATE_HUMAN = TODAY.strftime("%d %b %Y")
WEEKDAY = TODAY.strftime("%A")

DSA_DIR = "dsa"
QUOTE_FILE = "quotes/QUOTES_LOG.md"
STATE_FILE = ".github/daily_state.txt"


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
    os.makedirs("quotes", exist_ok=True)
    quote, author = fetch_quote()

    if not os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "w") as f:
            f.write("# Daily Quotes\n\nOne quote, every day.\n\n---\n")

    with open(QUOTE_FILE, "a") as f:
        f.write(f"\n### {WEEKDAY}, {DATE_HUMAN}\n> \"{quote}\"\n>\n> — *{author}*\n")

    print(f"[phase 4] appended quote by {author}")


def phase_5_cleanup():
    if random.random() < 0.40:
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


PHASES = {
    "1": phase_1_create_dsa,
    "2": phase_2_add_approach,
    "3": phase_3_add_solution,
    "4": phase_4_quote,
    "5": phase_5_cleanup,
}

if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "1"
    handler = PHASES.get(phase)
    if handler:
        handler()
    else:
        print(f"Unknown phase: {phase}")
        sys.exit(1)
