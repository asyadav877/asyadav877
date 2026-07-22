#!/usr/bin/env python3
"""Issue-driven tic-tac-toe for the profile README.

Usage: ttt.py 'ttt|move|<0-8>'   (called by GitHub Actions on issue open)
       ttt.py --selftest
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "games" / "state.json"
README = ROOT / "README.md"
REPO = "asyadav877/asyadav877"
WINS = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):
    for a, c, d in WINS:
        if b[a] and b[a] == b[c] == b[d]:
            return b[a]
    return None


def bot_move(b):
    # win if possible, else block, else center/corner/edge
    for mark in ("O", "X"):
        for line in WINS:
            vals = [b[i] for i in line]
            if vals.count(mark) == 2 and vals.count("") == 1:
                return line[vals.index("")]
    for i in (4, 0, 2, 6, 8, 1, 3, 5, 7):
        if not b[i]:
            return i
    return None


def render(state, status):
    cells = []
    for i, v in enumerate(state["board"]):
        if v == "X":
            cells.append("âŒ")
        elif v == "O":
            cells.append("â­•")
        else:
            url = (f"https://github.com/{REPO}/issues/new"
                   f"?title=ttt%7Cmove%7C{i}&body=Just+press+Submit+â€”+GitHub+Actions+plays+the+move+in+~30s.")
            cells.append(f'<a href="{url}">â¬œ</a>')
    rows = "\n".join(
        "<tr>" + "".join(f'<td align="center" width="60" height="60">{cells[r * 3 + c]}</td>' for c in range(3)) + "</tr>"
        for r in range(3))
    s = state["scores"]
    return (f"<!--ttt:board-->\n<div align=\"center\">\n\n**{status}**\n\n"
            f"<table>\n{rows}\n</table>\n\n"
            f"`scoreboard â†’ community {s['community']} Â· bot {s['bot']} Â· draws {s['draws']}`\n"
            f"</div>\n<!--ttt:end-->")


def save(state, status):
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    text = README.read_text()
    README.write_text(re.sub(r"<!--ttt:board-->.*?<!--ttt:end-->", render(state, status), text, flags=re.S))


def play(title):
    m = re.fullmatch(r"ttt\|move\|([0-8])", title.strip())
    if not m:
        print("not a ttt move, ignoring")
        return
    i = int(m.group(1))
    state = json.loads(STATE.read_text())
    b = state["board"]
    if b[i]:
        save(state, "That cell was taken â€” pick an empty one! You are âŒ")
        return
    b[i] = "X"
    status = "Your move â€” you are âŒ, bot is â­•"
    if winner(b) == "X":
        state["scores"]["community"] += 1
        state["board"] = [""] * 9
        status = "ðŸŽ‰ Community beat the bot! Fresh board â€” your move (âŒ)"
    elif "" not in b:
        state["scores"]["draws"] += 1
        state["board"] = [""] * 9
        status = "ðŸ¤ Draw! Fresh board â€” your move (âŒ)"
    else:
        b[bot_move(b)] = "O"
        if winner(b) == "O":
            state["scores"]["bot"] += 1
            state["board"] = [""] * 9
            status = "ðŸ¤– Bot wins â€” dattebayo! Fresh board, your move (âŒ)"
        elif "" not in b:
            state["scores"]["draws"] += 1
            state["board"] = [""] * 9
            status = "ðŸ¤ Draw! Fresh board â€” your move (âŒ)"
    save(state, status)


def selftest():
    assert winner(["X", "X", "X", "", "", "", "", "", ""]) == "X"
    assert winner(["O", "", "", "", "O", "", "", "", "O"]) == "O"
    assert winner([""] * 9) is None
    assert bot_move(["O", "O", "", "", "", "", "", "", ""]) == 2      # takes the win
    assert bot_move(["X", "X", "", "", "", "", "", "", ""]) == 2      # blocks
    assert bot_move([""] * 9) == 4                                     # center first
    print("selftest ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
    else:
        play(sys.argv[1] if len(sys.argv) > 1 else "")