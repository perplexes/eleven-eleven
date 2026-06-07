#!/usr/bin/env python3
"""
Scrape the 2024 Adult Compendium of Physical Activities (pacompendium.com)
into a structured dataset: SQLite + JSON.

Each category page hosts one HTML table of [code, MET, description] rows where
the 5-digit code's first two digits are the official category id. We pull every
category page, keep only real data rows (5-digit code + numeric MET), and emit:

  data/compendium.db    SQLite  (category + activity tables)
  data/compendium.json  list of {code, met, cat, desc}

Run:  python3 scripts/build_compendium.py            # fetch live
      PAC_CACHE=/tmp/pac python3 scripts/build_compendium.py   # parse cached html

Source: 2024 Adult Compendium of Physical Activities, https://pacompendium.com/
"""
import os, re, json, sqlite3, html, sys, urllib.request

BASE = "https://pacompendium.com"
OUT  = os.path.join(os.path.dirname(__file__), "..", "data")

# slug -> (official 2-digit category code, display name)
CATEGORIES = {
    "bicycling":            ("01", "Bicycling"),
    "conditioning-exercise":("02", "Conditioning Exercise"),
    "dancing":              ("03", "Dancing"),
    "fishing-hunting":      ("04", "Fishing and Hunting"),
    "home-activities":      ("05", "Home Activities"),
    "home-repair":          ("06", "Home Repair"),
    "inactivity":           ("07", "Inactivity"),
    "lawn-garden":          ("08", "Lawn and Garden"),
    "miscellaneous":        ("09", "Miscellaneous"),
    "music-playing":        ("10", "Music Playing"),
    "occupation":           ("11", "Occupation"),
    "running":              ("12", "Running"),
    "self-care":            ("13", "Self Care"),
    "sexual-activity":      ("14", "Sexual Activity"),
    "sports":               ("15", "Sports"),
    "transportation":       ("16", "Transportation"),
    "walking":              ("17", "Walking"),
    "water-activities":     ("18", "Water Activities"),
    "winter-activities":    ("19", "Winter Activities"),
    "religious-activities": ("20", "Religious Activities"),
    "volunteer-activities": ("21", "Volunteer Activities"),
    "video-games":          ("22", "Video Games & Screen Time"),
}

CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
ROW  = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
TAG  = re.compile(r"<[^>]+>")
WS   = re.compile(r"\s+")

def clean(s):
    s = TAG.sub("", s)
    s = html.unescape(s)
    s = s.replace("–", "-").replace("—", "-").replace("’", "'")
    return WS.sub(" ", s).strip()

def get_html(slug):
    cache = os.environ.get("PAC_CACHE")
    if cache:
        p = os.path.join(cache, f"{slug}.html")
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    req = urllib.request.Request(f"{BASE}/{slug}/", headers={"User-Agent": "Mozilla/5.0 compendium-scraper"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def parse(slug, page):
    out = []
    for rm in ROW.finditer(page):
        cells = [clean(c) for c in CELL.findall(rm.group(1))]
        if len(cells) < 3:
            continue
        code, met, desc = cells[0], cells[1], cells[2]
        if not re.fullmatch(r"\d{5}", code):       # skip headers / notes
            continue
        try:
            met = float(met)
        except ValueError:
            continue
        out.append({"code": code, "met": met, "cat": CATEGORIES[slug][1], "desc": desc})
    return out

def main():
    records, seen = [], set()
    for slug in CATEGORIES:
        rows = parse(slug, get_html(slug))
        kept = 0
        for r in rows:
            if r["code"] in seen:
                continue
            seen.add(r["code"]); records.append(r); kept += 1
        print(f"  {slug:22s} {kept:4d} activities", file=sys.stderr)
    records.sort(key=lambda r: r["code"])

    os.makedirs(OUT, exist_ok=True)
    compact = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "compendium.json"), "w", encoding="utf-8") as f:
        f.write(compact)
    # browser-loadable (works from file:// via <script src>, no fetch/CORS needed)
    with open(os.path.join(OUT, "compendium.js"), "w", encoding="utf-8") as f:
        f.write("window.COMPENDIUM=" + compact + ";\n")

    db = os.path.join(OUT, "compendium.db")
    if os.path.exists(db):
        os.remove(db)
    con = sqlite3.connect(db); cur = con.cursor()
    cur.execute("CREATE TABLE category (category_id TEXT PRIMARY KEY, category_name TEXT NOT NULL)")
    cur.execute("CREATE TABLE activity (code TEXT PRIMARY KEY, met REAL, category_id TEXT, description TEXT, "
                "FOREIGN KEY (category_id) REFERENCES category(category_id))")
    cur.executemany("INSERT INTO category VALUES (?,?)", [(cid, name) for cid, name in CATEGORIES.values()])
    cur.executemany("INSERT INTO activity VALUES (?,?,?,?)",
                    [(r["code"], r["met"], r["code"][:2], r["desc"]) for r in records])
    cur.execute("CREATE INDEX idx_met ON activity(met)")
    cur.execute("CREATE INDEX idx_cat ON activity(category_id)")
    con.commit()
    mets = [r["met"] for r in records]
    print(f"\nTOTAL: {len(records)} activities across {len(CATEGORIES)} categories", file=sys.stderr)
    print(f"MET range: {min(mets)} – {max(mets)}", file=sys.stderr)
    con.close()

if __name__ == "__main__":
    main()
