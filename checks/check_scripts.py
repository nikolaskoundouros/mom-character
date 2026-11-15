"""Every script parses, refers only to project/box paths (never a session scratchpad), and the refs it needs exist."""
import ast, pathlib, sys
P = pathlib.Path(__file__).resolve().parent.parent
bad = []
for f in list(P.glob("scripts/*.py")) + list(P.glob("live/*.py")):
    s = f.read_text()
    try:
        ast.parse(s)
    except SyntaxError as e:
        bad.append(f"{f.name}: does not parse ({e})")
    if "/scratchpad" in s or "/private/tmp/claude" in s:
        bad.append(f"{f.name}: points into a session scratchpad")
for f in P.glob("live/*.sh"):
    if "/scratchpad" in f.read_text():
        bad.append(f"{f.name}: points into a session scratchpad")
for t in ("64.5", "18.0", "62.0", "35.0"):
    if not (P / "refs" / "heads" / f"head_{t}.png").exists():
        bad.append(f"refs/heads/head_{t}.png missing")
print("\n".join(bad) or "scripts ok")
sys.exit(1 if bad else 0)
