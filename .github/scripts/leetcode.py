import json
import re
import sys
import urllib.request

USERNAME = "k0oda"
URL = "https://leetcode.com/graphql"
QUERY = """
query getUserProfile($username: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $username) {
    profile { ranking }
    submitStats { acSubmissionNum { difficulty count } }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        URL,
        data=json.dumps({"query": QUERY, "variables": {"username": USERNAME}}).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://leetcode.com/u/{USERNAME}/",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())["data"]


def bar(cur, tot, n=10):
    if not tot:
        return "░" * n
    filled = round(cur / tot * n)
    if cur > 0 and filled == 0:
        filled = 1
    return "█" * filled + "░" * (n - filled)


def pct(cur, tot):
    return round(cur / tot * 100) if tot else 0


def main():
    data = fetch()
    user = data.get("matchedUser")
    if not user:
        sys.exit("LeetCode user not found - README left untouched")

    totals = {i["difficulty"]: i["count"] for i in data["allQuestionsCount"]}
    solved = {
        i["difficulty"]: i["count"] for i in user["submitStats"]["acSubmissionNum"]
    }
    rank = user["profile"]["ranking"]
    rank_str = f"#{rank:,}" if rank else "unranked"

    lines = [
        "LEETCODE",
        "---------------",
        f"Solved : {solved['All']} / {totals['All']}",
    ]
    for d in ("Easy", "Medium", "Hard"):
        s, t = solved[d], totals[d]
        lines.append(f"{d:<6} : {s:<4} [{bar(s, t)}]")
    lines.append(f"Rank   : {rank_str}")

    block = "```fortran\n" + "\n".join(lines) + "\n```"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new = re.sub(
        r"<!-- LEETCODE:START -->.*?<!-- LEETCODE:END -->",
        lambda _: f"<!-- LEETCODE:START -->\n{block}\n<!-- LEETCODE:END -->",
        content,
        flags=re.DOTALL,
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new)


if __name__ == "__main__":
    main()
