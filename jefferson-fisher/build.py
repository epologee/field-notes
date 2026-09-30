#!/usr/bin/env python3
"""Render every quote in wisdom.csv as a poster and build the poster wall page."""
from pathlib import Path
import csv
import html

import poster

ROOT = Path(__file__).resolve().parent
LINK_LEAD_SECONDS = 2
HAND_SET_POSTERS = {
    3721: (["The conversation", "you're avoiding", "is the result", "you're choosing."], ["avoiding", "choosing"]),
}

rows = sorted(csv.DictReader((ROOT / "wisdom.csv").open()), key=lambda r: (-int(r["score"]), int(r["timestamp_s"])))
(ROOT / "posters").mkdir(exist_ok=True)
for stale in (ROOT / "posters").glob("*.svg"):
    stale.unlink()

cards = []
posters_at = {}
for number, row in enumerate(rows, 1):
    seconds = int(row["timestamp_s"])
    posters_at[seconds] = posters_at.get(seconds, 0) + 1
    name = f"{seconds}" if posters_at[seconds] == 1 else f"{seconds}-{posters_at[seconds]}"
    lines, accents = HAND_SET_POSTERS.get(seconds, (None, ()))
    (ROOT / "posters" / f"{name}.svg").write_text(poster.render(row, lines, accents))
    e = {k: html.escape(v) for k, v in row.items()}
    cards.append(f"""<li><a class="poster" href="posters/{name}.svg" target="_blank" rel="noopener"><img src="posters/{name}.svg" alt="{e['quote']}" loading="lazy" width="1080" height="1350"></a>
<p class="caption"><span>{number:03d} · {e['situation'].replace('-', ' ')}</span><a href="https://youtu.be/{poster.VIDEO_ID}?t={max(0, seconds - LINK_LEAD_SECONDS)}" target="_blank" rel="noopener">{poster.timecode(seconds)} ↗</a></p></li>""")

description = f"{len(rows)} posters of advice from Jefferson Fisher in conversation with Chris Williamson, each linked to its moment in the video."
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jefferson Fisher: The Quiet Art of Leading Any Conversation</title>
<meta name="description" content="{description}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Field notes">
<meta property="og:title" content="Jefferson Fisher: The Quiet Art of Leading Any Conversation"><meta property="og:description" content="{description}">
<meta property="og:url" content="https://epologee.github.io/field-notes/jefferson-fisher/index.html"><meta property="og:image" content="https://i.ytimg.com/vi/{poster.VIDEO_ID}/maxresdefault.jpg">
<meta property="og:image:width" content="1280"><meta property="og:image:height" content="720"><meta name="twitter:card" content="summary_large_image">
<style>
:root{{--ink:#211d19;--muted:#766e63;--desk:#d9d1c4;--paper:#f7f3eb;--rule:#cfc6b8;--accent:#a84f32;--serif:"Iowan Old Style",Baskerville,Georgia,serif;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;--mono:ui-monospace,monospace}}*{{box-sizing:border-box}}body{{margin:0;background:var(--desk);color:var(--ink);font:16px/1.55 var(--sans)}}header{{max-width:1190px;margin:auto;padding:30px 28px 20px;display:flex;justify-content:space-between;gap:20px;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}}header strong{{color:var(--ink)}}header a{{color:inherit;text-decoration:none}}header a:hover{{color:var(--accent)}}header span{{text-align:right}}main{{max-width:1190px;margin:auto;padding:0 28px 50px}}.intro{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:36px;align-items:center;background:var(--paper);padding:clamp(28px,5vw,56px);box-shadow:0 10px 34px #251d141c;margin-bottom:34px}}.kicker{{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}h1{{font:500 clamp(40px,6vw,68px)/1 var(--serif);letter-spacing:-.04em;margin:18px 0 16px}}h1 em{{color:var(--accent);font-weight:400}}.deck{{font:19px/1.45 var(--serif);color:#554c42;margin:0}}.screen{{position:relative;aspect-ratio:16/9;background:#000}}.screen iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}ol{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:28px 22px}}.poster{{display:block;box-shadow:0 10px 30px #251d1426;transition:transform .15s}}.poster:hover{{transform:translateY(-3px)}}.poster img{{display:block;width:100%;height:auto}}.caption{{display:flex;justify-content:space-between;gap:10px;margin:10px 2px 0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}.caption a{{font:11px var(--mono);letter-spacing:0;text-transform:none;color:var(--muted);text-decoration:none;white-space:nowrap}}.caption a:hover{{color:var(--accent)}}
@media(max-width:740px){{header{{padding:20px 16px 12px}}main{{padding:0 16px 30px}}.intro{{grid-template-columns:1fr;gap:24px;padding:26px 22px}}ol{{grid-template-columns:1fr}}}}
</style></head>
<body>
<header><strong><a href="../index.html">Field notes</a> · The quiet art</strong><span>Jefferson Fisher in conversation with Chris Williamson<br>Modern Wisdom · Published 4 May 2026 · 2h 11m</span></header>
<main>
<section class="intro"><div><div class="kicker">A poster wall · {len(rows)} posters</div><h1>The quiet art of<br><em>leading any conversation</em></h1><p class="deck">Advice from the conversation, set as posters and ordered by how well each line stands on its own. Every poster links to its moment in the video.</p></div>
<div class="screen"><iframe src="https://www.youtube.com/embed/{poster.VIDEO_ID}?rel=0&amp;playsinline=1" title="The Quiet Art of Leading Any Conversation" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div></section>
<ol>
{chr(10).join(cards)}
</ol>
</main></body></html>
"""
(ROOT / "index.html").write_text(page)
print(f"Built index.html with {len(rows)} posters")
