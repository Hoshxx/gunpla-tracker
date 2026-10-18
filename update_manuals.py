"""Builds manuals.json: an index of Bandai Hobby's web instruction manuals (names, dates and ids only).
Each id opens https://manual.bandai-hobby.net/pdf/<id>.pdf on Bandai's own site."""
import html as H, json, re, sys, time, urllib.request

BASE = "https://manual.bandai-hobby.net/"

def fetch(p):
    url = BASE + ("?page=%d" % p if p > 1 else "")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (GunplaTracker manual index)", "Accept-Language": "ja,en"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def parse(page):
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="[^"]*?/menus/detail/(\d+)"[^>]*>(.*?)</a>', page, re.S):
        i = int(m.group(1))
        if i in seen:
            continue
        txt = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        d = re.search(r"発売日\s*(\d{4})年\s*(\d{1,2})月(?:\s*(\d{1,2})日)?", txt)
        title = txt.split("発売日")[0].strip()
        date = ""
        if d:
            date = "%s-%02d" % (d.group(1), int(d.group(2))) + ("-%02d" % int(d.group(3)) if d.group(3) else "")
        if title:
            seen.add(i)
            out.append({"id": i, "t": title, "d": date})
    return out

def main():
    try:
        old = json.load(open("manuals.json", encoding="utf-8"))
    except Exception:
        old = []
    known = {x["id"]: x for x in old}
    streak = 0
    for p in range(1, 600):
        items = parse(fetch(p))
        if not items:
            if p == 1:
                sys.exit("No manuals parsed on page 1; the page layout may have changed. Leaving manuals.json unchanged.")
            break
        fresh = [x for x in items if x["id"] not in known]
        known.update({x["id"]: x for x in items})
        streak = streak + 1 if not fresh else 0
        if len(old) > 200 and streak >= 2:
            break
        time.sleep(1.0)
    out = sorted(known.values(), key=lambda x: (x["d"], x["id"]), reverse=True)
    json.dump(out, open("manuals.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(out), "manuals stored")

if __name__ == "__main__":
    main()
