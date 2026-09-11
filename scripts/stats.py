"""Reads the GeeksforGeeks profile and rewrites the stats block in README.md.

GfG has no public stats API. The profile page is server-rendered by Next.js, and the numbers
are already in the HTML payload as JSON before any JavaScript runs -- so a plain HTTP request is
enough and no headless browser is needed.

Run by .github/workflows/stats.yml once a day. It only commits when a number actually changed,
so the history stays a record of real progress rather than a daily no-op commit.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROFILE = "https://www.geeksforgeeks.org/profile/{handle}"
README = Path(__file__).resolve().parents[1] / "README.md"

START = "<!-- stats:start -->"
END = "<!-- stats:end -->"

# A browser User-Agent is required; GfG returns a challenge page to the default urllib one.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

FIELDS = {
    "total_problems_solved": int,
    "score": int,
    "institute_rank": int,
    "institute_name": str,
    "pod_correct_submissions_count": int,
    "pod_solved_longest_streak": int,
    "pod_solved_current_streak": int,
}


def fetch(handle: str) -> dict:
    request = urllib.request.Request(PROFILE.format(handle=handle), headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read().decode("utf-8", errors="ignore")

    # The payload is embedded as an escaped JSON string inside the page, so unescape first.
    text = raw.encode().decode("unicode_escape", errors="ignore")

    stats: dict = {}
    for key, cast in FIELDS.items():
        match = re.search(rf'"{key}"\s*:\s*"?([^,"}}]+)', text)
        if not match:
            continue
        value = match.group(1).strip()
        try:
            stats[key] = cast(value)
        except ValueError:
            continue

    if "total_problems_solved" not in stats:
        # Fail loudly. Silently writing an empty table would quietly blank the README.
        raise SystemExit(
            "could not find stats in the profile page -- GfG may have changed its markup"
        )

    # The difficulty split (Hard/Medium/Easy/Basic) is fetched by the page's own JavaScript
    # after load, so it is usually absent from this payload and the block below renders without
    # it. Getting it would mean running a headless browser in CI to update one line, which is
    # not worth the dependency -- the totals above are the numbers that move daily anyway.
    difficulty = {}
    for level in ("School", "Basic", "Easy", "Medium", "Hard"):
        match = re.search(rf'"{level}"\s*:\s*(\d+)', text)
        if match:
            difficulty[level] = int(match.group(1))
    stats["difficulty"] = difficulty
    return stats


def render(stats: dict, handle: str) -> str:
    solved = stats["total_problems_solved"]
    difficulty = stats.get("difficulty", {})
    hard = difficulty.get("Hard")
    medium = difficulty.get("Medium")

    lines = [
        START,
        "",
        "<div align=\"center\">",
        "",
        "| Problems solved | Coding score | Institute rank | Longest streak |",
        "|:---:|:---:|:---:|:---:|",
        f"| **{solved}** | **{stats.get('score', '—')}** | "
        f"**#{stats.get('institute_rank', '—')}** | "
        f"**{stats.get('pod_solved_longest_streak', '—')} days** |",
        "",
        "</div>",
        "",
    ]

    if hard is not None and medium is not None:
        split = " · ".join(
            f"{level} {difficulty[level]}"
            for level in ("Hard", "Medium", "Easy", "Basic")
            if level in difficulty
        )
        lines.append(f"**{hard + medium} of those {solved} are Medium or Hard** — {split}.")
        lines.append("")

    lines += [
        f"{stats.get('pod_correct_submissions_count', 0)} problems-of-the-day solved · "
        f"current streak {stats.get('pod_solved_current_streak', 0)} days · "
        f"{stats.get('institute_name', '')}".rstrip(" ·· "),
        "",
        f"[→ GeeksforGeeks profile](https://www.geeksforgeeks.org/profile/{handle})",
        "",
        f"<sub>Updated {datetime.now(timezone.utc):%d %b %Y} · "
        "refreshed daily by [stats.yml](.github/workflows/stats.yml)</sub>",
        "",
        END,
    ]
    return "\n".join(lines)


def main() -> None:
    handle = sys.argv[1] if len(sys.argv) > 1 else "ankitnehra20cse"
    stats = fetch(handle)

    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit(f"README.md is missing the {START} / {END} markers")

    updated = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: render(stats, handle),
        readme,
        flags=re.S,
    )

    # Compare everything except the timestamp line, so an unchanged day is not a commit.
    def strip_date(text: str) -> str:
        return re.sub(r"<sub>Updated .*?</sub>", "", text, flags=re.S)

    if strip_date(updated) == strip_date(readme):
        print("no change")
        return

    README.write_text(updated, encoding="utf-8")
    print("updated:", json.dumps({k: v for k, v in stats.items() if k != "difficulty"}))


if __name__ == "__main__":
    main()
