import sys, re, html, urllib.request
for path in sys.argv[1:]:
    url = "https://docs.blender.org/manual/en/5.3/" + path
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode()
    except Exception as e:
        print("##", path, "ERROR", e); continue
    m = re.search(r'<div itemprop="articleBody">(.*?)<footer', raw, re.S) or re.search(r'<article[^>]*>(.*?)</article>', raw, re.S)
    body = m.group(1) if m else raw
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
    body = re.sub(r"<(h\d)[^>]*>", "\n## ", body); body = re.sub(r"<(li|dt)[^>]*>", "\n- ", body)
    body = re.sub(r"<(p|dd|br|tr)[^>]*>", "\n", body); body = re.sub(r"<[^>]+>", "", body)
    text = re.sub(r"\n\s*\n+", "\n", html.unescape(body)).strip()
    name = path.replace("/", "_").replace(".html", ".txt")
    open(name, "w").write(text); print("##", path, len(text), "chars")
