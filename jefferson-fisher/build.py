#!/usr/bin/env python3
"""Render every quote in wisdom.csv as a poster and build the poster wall page."""
from pathlib import Path
import csv
import html
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT.parent)]
import poster  # noqa: E402
from field_notes import render  # noqa: E402
from field_notes.episode import LEAD_S, Item, Quote, breaks  # noqa: E402

SLUG = "jefferson-fisher"
TITLE = "Jefferson Fisher: The Quiet Art of Leading Any Conversation"
ORDERED = False
HAND_SET_POSTERS = {
    3721: (["The conversation", "you're avoiding", "is the result", "you're choosing."], ["avoiding", "choosing"]),
}
SITE_SCRIPT = (ROOT / "site.js").read_text()


def rows():
    return sorted(csv.DictReader((ROOT / "wisdom.csv").open()), key=lambda r: (-int(r["score"]), int(r["timestamp_s"])))


def items():
    return [Item(row["quote"][:48], int(row["timestamp_s"]), [Quote(row["quote"], int(row["timestamp_s"]), row["wording"] == "verbatim")]) for row in rows()]


def prose():
    for row in rows():
        for text in (row["quote"], row["paraphrase"], poster.context_for(row)):
            yield row["quote"][:48], poster.curl_quotes(text)


def build():
    rows_ = rows()
    (ROOT / "posters").mkdir(exist_ok=True)
    for stale in (ROOT / "posters").glob("*.svg"):
        stale.unlink()
    cards = []
    docs = []
    posters_at = {}
    for number, row in enumerate(rows_, 1):
        seconds = int(row["timestamp_s"])
        posters_at[seconds] = posters_at.get(seconds, 0) + 1
        name = f"{seconds}" if posters_at[seconds] == 1 else f"{seconds}-{posters_at[seconds]}"
        lines, accents = HAND_SET_POSTERS.get(seconds, (None, ()))
        (ROOT / "posters" / f"{name}.svg").write_text(poster.render(row, lines, accents))
        e = {k: html.escape(v) for k, v in row.items()}
        cards.append(CARD.format(name=name, seconds=seconds, quote=e["quote"], number=number,
                                 situation=e["situation"].replace("-", " "), link=f"https://youtu.be/{poster.VIDEO_ID}?t={max(0, seconds - LEAD_S)}",
                                 timecode=poster.timecode(seconds)))
        docs.append({"text": " ".join(poster.curl_quotes(t) for t in (row["quote"], row["situation"].replace("-", " "), row["paraphrase"], poster.context_for(row)))})
    index = ROOT / "transcript-index.json"
    data = {
        "lead": LEAD_S,
        "docs": docs,
        "breaks": [vars(b) for b in breaks(ROOT)],
        "transcript": json.loads(index.read_text()) if index.exists() else {},
    }
    description = f"{len(rows_)} posters of advice from Jefferson Fisher in conversation with Chris Williamson, each linked to its moment in the video."
    template = PAGE.replace("@@CARDS@@", "\n".join(cards)).replace("@@COUNT@@", str(len(rows_)))
    render.write(SLUG, render.page(template, SLUG, TITLE, description, data))
    return f"Built {SLUG}/index.html with {len(rows_)} posters"


CARD = """<li id="p{name}" data-seconds="{seconds}"><a class="poster" href="#p{name}"><img src="posters/{name}.svg" alt="{quote}" loading="lazy" width="1080" height="1350"></a>
<p class="caption"><span><a class="file" href="posters/{name}.svg" target="_blank" rel="noopener" title="Open this poster on its own">{number:03d}</a> · {situation}</span><a class="time" href="{link}" target="_blank" rel="noopener">{timecode} ↗</a></p></li>"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<!-- field-notes:head -->
<style>
:root{--ink:#1f2b3d;--muted:#5e6b7d;--desk:#ede3b0;--paper:#fbf5d4;--rule:#a9c0d8;--accent:#c33a2e;--serif:"Iowan Old Style",Baskerville,Georgia,serif;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;--mono:ui-monospace,monospace}*{box-sizing:border-box}body{margin:0;background:var(--desk);color:var(--ink);font:16px/1.55 var(--sans)}header{max-width:1190px;margin:auto;padding:30px 28px 20px;display:flex;justify-content:space-between;gap:20px;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}header strong{color:var(--ink)}header a{color:inherit;text-decoration:none}header a:hover{color:var(--accent)}header span{text-align:right}main{max-width:1190px;margin:auto;padding:0 28px 50px}.intro{position:relative;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:36px;align-items:center;background:var(--paper);padding:clamp(28px,5vw,56px);box-shadow:0 10px 34px #1f2b3d1f;margin-bottom:34px}.intro::before{content:"";position:absolute;top:0;bottom:0;left:clamp(12px,2.6vw,30px);width:3px;border-left:1px solid var(--accent);border-right:1px solid var(--accent)}.kicker{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}h1{font:500 clamp(40px,6vw,68px)/1 var(--serif);letter-spacing:-.04em;margin:18px 0 16px}h1 em{color:var(--accent);font-weight:400}.deck{font:19px/1.45 var(--serif);color:#3b4658;margin:0}.slot{position:relative;aspect-ratio:16/9;background:#000}.screen{position:absolute;inset:0;background:#000}.screen iframe,.screen>div{position:absolute;inset:0;width:100%;height:100%;border:0}.docked .screen{position:fixed;inset:auto 16px 16px auto;width:clamp(200px,60vw,360px);aspect-ratio:16/9;z-index:5;box-shadow:0 12px 40px #0006}.docked main{padding-bottom:calc(clamp(200px,60vw,360px)*9/16 + 40px)}.order{margin:22px 0 0;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}.order button{font:inherit;letter-spacing:inherit;text-transform:inherit;color:var(--muted);background:none;border:1px solid var(--rule);padding:6px 9px;margin-left:4px;cursor:pointer}.order button[aria-pressed=true]{color:var(--ink);border-color:var(--ink)}li.current .poster{outline:3px solid var(--accent);outline-offset:5px}ol.wall{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:28px 22px}.poster{display:block;box-shadow:0 10px 30px #1f2b3d29;transition:transform .15s}.poster:hover{transform:translateY(-3px)}.poster img{display:block;width:100%;height:auto}.caption{display:flex;justify-content:space-between;gap:10px;margin:10px 2px 0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}.caption .time{font:11px var(--mono);letter-spacing:0;text-transform:none;color:var(--muted);text-decoration:none;white-space:nowrap}.caption a:hover{color:var(--accent)}.caption .file{color:inherit;text-decoration:underline dotted;text-underline-offset:3px}.find{margin:14px 0 0}.find input{font:14px var(--sans);width:min(100%,380px);padding:8px 10px;border:1px solid var(--rule);border-radius:0;background:#ffffff80;color:var(--ink)}.find input:focus{outline:none;border-color:var(--ink)}.spoken{margin:0 0 26px;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}.spoken button{font:11px var(--mono);letter-spacing:0;text-transform:none;color:var(--ink);background:none;border:1px solid var(--rule);padding:5px 8px;margin:6px 6px 0 0;cursor:pointer}.spoken button:hover{border-color:var(--ink)}li.break{grid-column:1/-1;border-top:1px dashed var(--rule);padding:9px 2px 0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}li.break span{color:var(--ink);margin-right:8px}li.break.playing{border-top-style:solid;border-top-color:var(--muted)}
@media print{@page{size:A4;margin:12mm}body{background:white}header span{text-align:left}.slot,.screen,.order,.find,.spoken,li.break{display:none!important}.intro{display:block;box-shadow:none;padding:0 0 8mm}.intro::before{display:none}ol.wall{grid-template-columns:repeat(2,1fr);gap:8mm}li{break-inside:avoid}.poster{box-shadow:none;outline:1px solid #ddd}li.current .poster{outline:1px solid #ddd}}
@media(max-width:740px){header{padding:20px 16px 12px}main{padding:0 16px 30px}.intro{grid-template-columns:1fr;gap:24px;padding:26px 22px}ol.wall{grid-template-columns:1fr}}
</style></head>
<body>
<header><strong><a href="../index.html">Field notes</a> · The quiet art</strong><span>Jefferson Fisher in conversation with Chris Williamson<br>Modern Wisdom · <!-- field-notes:published --> · 2h 11m</span></header>
<main>
<section class="intro"><div><div class="kicker">A poster wall · @@COUNT@@ posters</div><h1>The quiet art of<br><em>leading any conversation</em></h1><p class="deck">Advice from the conversation, set as posters and ordered by how well each line stands on its own. Every poster links to its moment in the video.</p><p class="order">Order <button data-order="score" aria-pressed="true">Best first</button><button data-order="time" aria-pressed="false">As spoken</button></p><p class="find"><input id="q" type="search" placeholder="Search the posters and the conversation" aria-label="Search the posters and the conversation" autocomplete="off"></p></div>
<div class="slot"><div class="screen"><div id="player"></div></div></div></section>
<div id="spoken" class="spoken" hidden></div><p id="empty" class="spoken" hidden>No poster or moment mentions these words.</p>
<ol class="wall">
@@CARDS@@
</ol>
</main>
<!-- field-notes:runtime -->
<script>
@@SCRIPT@@
</script></body></html>
""".replace("@@SCRIPT@@", SITE_SCRIPT)


if __name__ == "__main__":
    print(build())
