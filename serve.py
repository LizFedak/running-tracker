#!/usr/bin/env python3
"""Tiny local running-plan viewer. No dependencies.

    python3 serve.py          -> http://localhost:8000
    python3 serve.py 8080     -> custom port
    python3 serve.py --build  -> write static site to public/ (used by Vercel)

Reads weeks/*.md on every request, so just edit files and refresh.
"""
import html
import re
import sys
import webbrowser
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).parent
WEEKS = ROOT / "weeks"
BUILDING = "--build" in sys.argv  # deployed site leaves out profile.md (personal info)
PORT = next((int(a) for a in sys.argv[1:] if a.isdigit()), 8000)

CSS = """
body{font:15px/1.45 -apple-system,system-ui,sans-serif;color:#111;max-width:8in;margin:0 auto;padding:1.5rem}
nav{display:flex;gap:1.2rem;align-items:center;border-bottom:1px solid #ddd;padding-bottom:.6rem;margin-bottom:1.5rem}
nav button{margin-left:auto;font:inherit;padding:.2rem .8rem;cursor:pointer}
a{color:#0645ad}
h1{font-size:1.5rem;margin:.2rem 0}
h2{font-size:1.1rem;margin:1.1rem 0 .3rem;border-bottom:1px solid #ccc;padding-bottom:.1rem}
h3{font-size:1rem;margin:.8rem 0 .2rem}
p,ul,ol{margin:.35rem 0}
table{border-collapse:collapse;width:100%;margin:.5rem 0}
th,td{border:1px solid #999;padding:.3rem .5rem;text-align:left;vertical-align:top}
th{background:#f2f2f2}
.n{text-align:right;font-variant-numeric:tabular-nums}
tr.total td{font-weight:600;border-top:2px solid #333}
tr.now td{background:#fffbe6}
.summary{color:#444;margin-bottom:.6rem}
.tag{font-size:.75rem;border:1px solid #999;border-radius:3px;padding:0 .3rem;margin-left:.4rem}
ul.check{list-style:none;padding-left:.8rem}
blockquote{border-left:3px solid #ccc;margin:.5rem 0;padding-left:.8rem;color:#444}
code{background:#f4f4f4;padding:0 .2rem}
.page{break-before:page}
.page:first-of-type{break-before:auto}
@media screen and (max-width:640px){
  body{padding:.8rem;font-size:15px}
  nav{gap:.9rem}
  nav button{display:none}
  .tablewrap{overflow-x:auto}
  th,td{padding:.25rem .35rem}
}
/* letter paper, extra left margin for binder holes */
@page{size:letter;margin:.6in .6in .6in .9in}
@media print{
  nav{display:none}
  body{padding:0;max-width:none;font-size:11pt}
  a{color:inherit;text-decoration:none}
  th,tr.now td{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  tr{break-inside:avoid}
  h2,h3{break-after:avoid}
}
"""


# ---------- parsing ----------

def parse(path):
    """Split '---' frontmatter (key: value lines) from markdown body."""
    text = path.read_text()
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.split("#")[0].strip()
        text = text[m.end():]
    return meta, text


def num(s):
    m = re.search(r"\d+(?:\.\d+)?", s or "")
    return float(m.group()) if m else None


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def column_total(text, prefix):
    """Sum a table column whose header starts with `prefix` (e.g. 'actual')."""
    total, found, col = 0.0, False, None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            col = None
            continue
        row = cells(s)
        if col is None:  # header row
            col = next((j for j, c in enumerate(row) if c.lower().startswith(prefix)), -1)
            continue
        if col < 0 or col >= len(row) or re.fullmatch(r"[:\- ]+", row[col]):
            continue
        if row[0].lower().strip("* ").startswith("total"):
            continue
        n = num(row[col])
        if n is not None:
            total += n
            found = True
    return total if found else None


def fmt(x):
    return "—" if x is None else f"{round(x, 1):g}"


# ---------- minimal markdown ----------

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


BLOCK_START = re.compile(r"(#{1,6}\s|\||[-*]\s|\d+\.\s|>|-{3,}$)")


def md(text):
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
        elif m := re.match(r"(#{1,6})\s+(.*)", s):
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            i += 1
        elif re.fullmatch(r"-{3,}|\*{3,}", s):
            out.append("<hr>")
            i += 1
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            head = rows[0]
            body = [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            t = ["<table><thead><tr>", *(f"<th>{inline(c)}</th>" for c in head), "</tr></thead><tbody>"]
            for r in body:
                cls = ' class="total"' if r and r[0].lower().strip("* ").startswith("total") else ""
                t.append(f"<tr{cls}>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append('<div class="tablewrap">' + "".join(t) + "</tbody></table></div>")
        elif re.match(r"([-*]|\d+\.)\s", s):
            tag = "ol" if s[0].isdigit() else "ul"
            items = []
            while i < len(lines) and (m := re.match(r"\s*([-*]|\d+\.)\s+(.*)", lines[i])):
                items.append(m.group(2))
                i += 1
            check = all(re.match(r"\[[ xX]\]", it) for it in items)
            lis = []
            for it in items:
                if check:
                    box = "☑" if it[1] in "xX" else "☐"
                    it_html = f"{box} {inline(it[3:].strip())}"
                else:
                    it_html = inline(it)
                lis.append(f"<li>{it_html}</li>")
            cls = ' class="check"' if check else ""
            out.append(f"<{tag}{cls}>{''.join(lis)}</{tag}>")
        elif s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
        else:
            buf = [s]
            i += 1
            while i < len(lines) and lines[i].strip() and not BLOCK_START.match(lines[i].strip()):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


# ---------- data ----------

def load_week(path):
    meta, body = parse(path)
    goal = num(meta.get("goal_miles"))
    if goal is None:
        goal = column_total(body, "planned")
    done = num(meta.get("completed_miles"))
    if done is None:
        done = column_total(body, "actual")
    try:
        start = date.fromisoformat(path.stem)
        label = start.strftime("%b %-d, %Y")
        now = start <= date.today() <= start + timedelta(days=6)
    except ValueError:
        label, now = path.stem, False
    return {"stem": path.stem, "label": label, "now": now, "focus": meta.get("focus", ""),
            "goal": goal, "done": done, "body": body}


def load_weeks():
    if not WEEKS.exists():
        return []
    return [load_week(p) for p in sorted(WEEKS.glob("*.md")) if not p.name.startswith("_")]


def pct(w):
    if w["goal"] and w["done"] is not None:
        return f"{round(100 * w['done'] / w['goal'])}%"
    return "—"


# ---------- pages ----------

def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<nav><a href="/">Weeks</a><a href="/progress">Progress</a>{"" if BUILDING else '<a href="/profile">Profile</a>'}
<button onclick="print()">Print this page</button></nav>
<main>{body}</main></body></html>"""


def weeks_table(weeks):
    if not weeks:
        return "<p>No weeks yet. Ask Claude to “plan next week” (see CLAUDE.md).</p>"
    rows = []
    for w in weeks:
        tag = '<span class="tag">this week</span>' if w["now"] else ""
        rows.append(
            f'<tr{" class=now" if w["now"] else ""}><td><a href="/week/{w["stem"]}">{w["label"]}</a>{tag}</td>'
            f'<td>{html.escape(w["focus"])}</td><td class="n">{fmt(w["goal"])}</td>'
            f'<td class="n">{fmt(w["done"])}</td><td class="n">{pct(w)}</td></tr>')
    tg = sum(w["goal"] or 0 for w in weeks)
    logged = [w["done"] for w in weeks if w["done"] is not None]
    td = sum(logged) if logged else None
    rows.append(f'<tr class="total"><td>Total ({len(weeks)} weeks)</td><td></td>'
                f'<td class="n">{fmt(tg)}</td><td class="n">{fmt(td)}</td>'
                f'<td class="n">{f"{round(100 * td / tg)}%" if tg and td is not None else "—"}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th>Week of</th><th>Focus</th><th class="n">Goal mi</th>'
            '<th class="n">Completed mi</th><th class="n">%</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>")


def week_section(w):
    bits = [f"Focus: {html.escape(w['focus'])}"] if w["focus"] else []
    bits += [f"Goal: {fmt(w['goal'])} mi", f"Completed: {fmt(w['done'])} mi ({pct(w)})"]
    return (f'<section class="page"><h1>Week of {w["label"]}</h1>'
            f'<p class="summary">{" · ".join(bits)}</p>{md(w["body"])}</section>')


def index_page():
    return page("Running weeks", f'<section class="page"><h1>Running weeks</h1>{weeks_table(load_weeks())}</section>')


def week_page(stem):
    path = WEEKS / f"{stem}.md"
    if not path.is_file():
        raise FileNotFoundError
    w = load_week(path)
    return page(f"Week of {w['label']}", week_section(w))


def doc_page(name):
    path = ROOT / f"{name}.md"
    body = md(parse(path)[1]) if path.exists() else f"<p>No {name}.md yet.</p>"
    return page(name.title(), f'<section class="page">{body}</section>')



class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        try:
            if path == "/":
                body = index_page()
            elif path in ("/progress", "/profile"):
                body = doc_page(path[1:])
            elif m := re.fullmatch(r"/week/([\w-]+)", path):
                body = week_page(m.group(1))
            else:
                raise FileNotFoundError
            code = 200
        except FileNotFoundError:
            code, body = 404, page("Not found", "<p>Not found. <a href='/'>Back to weeks</a></p>")
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def build(out=ROOT / "public"):
    """Write every page as static HTML. URLs match the local server via Vercel cleanUrls."""
    import shutil
    shutil.rmtree(out, ignore_errors=True)
    (out / "week").mkdir(parents=True)
    (out / "index.html").write_text(index_page())
    (out / "progress.html").write_text(doc_page("progress"))
    weeks = load_weeks()
    for w in weeks:
        (out / "week" / f"{w['stem']}.html").write_text(page(f"Week of {w['label']}", week_section(w)))
    print(f"Built {len(weeks)} weeks -> {out}")


if __name__ == "__main__" and BUILDING:
    build()
elif __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print(f"Running tracker at {url}  (Ctrl+C to stop)")
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
