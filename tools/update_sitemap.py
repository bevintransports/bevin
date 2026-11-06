#!/usr/bin/env python3
"""Rebuild docs/sitemap.xml from the HTML files in docs/, using each file's
real last-commit date from git. Run before every push:  python3 tools/update_sitemap.py
Excludes the Google verification file. Tamil (-ta) pages are included."""
import glob, os, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BASE = "https://bevintransports.in/"

def last_date(path):
    rel = os.path.relpath(path, ROOT)
    out = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=short", "--", rel],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    # uncommitted edits count as today
    dirty = subprocess.run(["git", "status", "--porcelain", "--", rel],
                           cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty or not out:
        return datetime.date.today().isoformat()
    return out

files = sorted(f for f in glob.glob(os.path.join(DOCS, "*.html"))
               if not os.path.basename(f).startswith("google"))
def prio(name):
    if name == "index.html": return "1.0", "weekly"
    if name.startswith("guide") : return "0.8", "monthly"
    if name == "find-us.html": return "0.7", "monthly"
    return "0.9", "weekly"

# homepage first
files.sort(key=lambda f: (os.path.basename(f) != "index.html", os.path.basename(f)))
rows = []
for f in files:
    name = os.path.basename(f)
    loc = BASE if name == "index.html" else BASE + name
    p, cf = prio(name)
    rows.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{last_date(f)}</lastmod>\n"
                f"    <changefreq>{cf}</changefreq>\n    <priority>{p}</priority>\n  </url>")
xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")
open(os.path.join(DOCS, "sitemap.xml"), "w").write(xml)
print(f"sitemap.xml rebuilt with {len(rows)} URLs")
