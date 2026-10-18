"""Reads the latest posts from en.gundam-official.com/news and merges them into news.json.
The headlines are embedded in the page's own code (Next.js 'self.__next_f.push' chunks)."""
import json, re, sys, urllib.request

URL = "https://en.gundam-official.com/news"
KEEP = 100

def parse(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,\s*"(.*?)"\]\)', html, re.S)
    text = "".join(json.loads('"' + c + '"') for c in chunks)
    i = text.find('"newsResponse":{"data":')
    if i < 0:
        raise ValueError("newsResponse not found; the page layout may have changed")
    arr, _ = json.JSONDecoder().raw_decode(text, text.index("[", i))
    return [{"id": d["documentId"], "date": d["displayDatetime"], "title": d["title"], "url": d["url"]}
            for d in arr if d.get("documentId") and d.get("title")]

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (GunplaTracker news reader)", "Accept-Language": "en"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    fresh = parse(html)
    if not fresh:
        sys.exit("No posts parsed; leaving news.json unchanged")
    try:
        old = json.load(open("news.json", encoding="utf-8"))
    except Exception:
        old = []
    merged = {n["id"]: n for n in old}
    merged.update({n["id"]: n for n in fresh})
    items = sorted(merged.values(), key=lambda n: n["date"], reverse=True)[:KEEP]
    json.dump(items, open("news.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(fresh)} fetched, {len(items)} stored")

if __name__ == "__main__":
    main()
