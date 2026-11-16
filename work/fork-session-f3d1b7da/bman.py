#!/usr/bin/env python3
"""Search the offline Blender manual (5.3, official HTML package) on the box.
  bman "curl hair"            pages ranked by how often all words appear, with the online link and a snippet
  bman -p modeling/geometry_nodes/hair/guides/curl_hair_curves   print that page's text
  bman --build               (re)build the plain-text copy from html/ (run once after a new download)
Text lives in ~/Documents/blender-manual/text/, one .txt per page, same paths as the online manual."""
import html, os, re, sys
from pathlib import Path
ROOT = Path.home() / "Documents" / "blender-manual"
HTML, TEXT = ROOT / "html" / "blender_manual_v530_en.html", ROOT / "text"
URL = "https://docs.blender.org/manual/en/latest/"

def body(raw):
    m = re.search(r'<div itemprop="articleBody">(.*?)<footer', raw, re.S) or re.search(r"<article[^>]*>(.*?)</article>", raw, re.S)
    b = m.group(1) if m else raw
    b = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", b, flags=re.S)
    b = re.sub(r"<(h\d)[^>]*>", "\n## ", b); b = re.sub(r"<(li|dt)[^>]*>", "\n- ", b)
    b = re.sub(r"<(p|dd|br|tr)[^>]*>", "\n", b); b = re.sub(r"<[^>]+>", "", b)
    return re.sub(r"\n\s*\n+", "\n", html.unescape(b)).replace("¶", "").strip()

if sys.argv[1:2] == ["--build"]:
    n = 0
    for f in HTML.rglob("*.html"):
        rel = f.relative_to(HTML).with_suffix(".txt")
        out = TEXT / rel; out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body(f.read_text(errors="ignore"))); n += 1
    print(n, "pages written to", TEXT); sys.exit()
if sys.argv[1:2] == ["-p"]:
    p = sys.argv[2].removesuffix(".html").removesuffix(".txt")
    print(URL + p + ".html\n"); print((TEXT / (p + ".txt")).read_text()); sys.exit()
words = [w.lower() for w in " ".join(sys.argv[1:]).split()]
hits = []
for f in TEXT.rglob("*.txt"):
    t = f.read_text(); low = t.lower()
    if all(w in low for w in words):
        title = (t.splitlines() or [""])[0].lstrip("# ").strip()
        score = sum(low.count(w) for w in words) + 20 * sum(w in title.lower() for w in words)
        hits.append((score, f, title, low))
for score, f, title, low in sorted(hits, key=lambda h: -h[0])[:12]:
    rel = f.relative_to(TEXT).with_suffix("")
    i = low.find(words[0]); snip = f.read_text()[max(0, i - 80): i + 160].replace("\n", " ")
    print(f"{title}  [{rel}]\n   {URL}{rel}.html\n   ...{snip}...\n")
print(f"{len(hits)} pages match" if hits else "no page matches all words")
