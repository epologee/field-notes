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
    cards.append(f"""<li data-seconds="{seconds}"><a class="poster" href="posters/{name}.svg" target="_blank" rel="noopener"><img src="posters/{name}.svg" alt="{e['quote']}" loading="lazy" width="1080" height="1350"></a>
<p class="caption"><span>{number:03d} · {e['situation'].replace('-', ' ')}</span><a href="https://youtu.be/{poster.VIDEO_ID}?t={max(0, seconds - LINK_LEAD_SECONDS)}" target="_blank" rel="noopener">{poster.timecode(seconds)} ↗</a></p></li>""")

PLAYER_SCRIPT = """
const video='%s',lead=%d,wall=document.querySelector('ol'),cards=[...wall.children],slot=document.querySelector('.slot');
let player,started=false,following=null,hold=null,lastT=0,humanUntil=0,current=null;
new IntersectionObserver(([e])=>document.body.classList.toggle('docked',!e.isIntersecting)).observe(slot);
function order(kind){(kind==='time'?[...cards].sort((a,b)=>a.dataset.seconds-b.dataset.seconds):cards).forEach(li=>wall.append(li));document.querySelectorAll('[data-order]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.order===kind))}
document.querySelectorAll('[data-order]').forEach(b=>b.onclick=()=>order(b.dataset.order));
for(const ev of ['wheel','touchmove','keydown'])addEventListener(ev,()=>humanUntil=Date.now()+3000,{passive:true});
const cardAt=t=>cards.reduce((at,li)=>li.dataset.seconds-lead<=t&&(!at||+li.dataset.seconds>+at.dataset.seconds)?li:at,null);
function follow(){let t=player.getCurrentTime();if(hold){if(Math.abs(t-hold.t)>30&&Date.now()-hold.at<180000)return;hold=null}else if(lastT>30&&t<5){hold={t:lastT,at:Date.now()};return}lastT=t;let li=cardAt(t);if(li===current)return;current?.classList.remove('current');current=li;if(!li)return;li.classList.add('current');if(Date.now()>humanUntil)li.scrollIntoView({behavior:'smooth',block:'center'})}
window.onYouTubeIframeAPIReady=()=>{player=new YT.Player('player',{videoId:video,playerVars:{rel:0,playsinline:1},events:{onStateChange:e=>{clearInterval(following);if(e.data!==YT.PlayerState.PLAYING)return;if(!started){started=true;order('time')}following=setInterval(follow,1000);follow()}}})};
{let tag=document.createElement('script');tag.src='https://www.youtube.com/iframe_api';document.head.append(tag)}
""" % (poster.VIDEO_ID, LINK_LEAD_SECONDS)

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
:root{{--ink:#211d19;--muted:#766e63;--desk:#d9d1c4;--paper:#f7f3eb;--rule:#cfc6b8;--accent:#a84f32;--serif:"Iowan Old Style",Baskerville,Georgia,serif;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;--mono:ui-monospace,monospace}}*{{box-sizing:border-box}}body{{margin:0;background:var(--desk);color:var(--ink);font:16px/1.55 var(--sans)}}header{{max-width:1190px;margin:auto;padding:30px 28px 20px;display:flex;justify-content:space-between;gap:20px;font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}}header strong{{color:var(--ink)}}header a{{color:inherit;text-decoration:none}}header a:hover{{color:var(--accent)}}header span{{text-align:right}}main{{max-width:1190px;margin:auto;padding:0 28px 50px}}.intro{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:36px;align-items:center;background:var(--paper);padding:clamp(28px,5vw,56px);box-shadow:0 10px 34px #251d141c;margin-bottom:34px}}.kicker{{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}h1{{font:500 clamp(40px,6vw,68px)/1 var(--serif);letter-spacing:-.04em;margin:18px 0 16px}}h1 em{{color:var(--accent);font-weight:400}}.deck{{font:19px/1.45 var(--serif);color:#554c42;margin:0}}.slot{{position:relative;aspect-ratio:16/9;background:#000}}.screen{{position:absolute;inset:0;background:#000}}.screen iframe,.screen>div{{position:absolute;inset:0;width:100%;height:100%;border:0}}.docked .screen{{position:fixed;inset:auto 16px 16px auto;width:clamp(200px,60vw,360px);aspect-ratio:16/9;z-index:5;box-shadow:0 12px 40px #0006}}.docked main{{padding-bottom:calc(clamp(200px,60vw,360px)*9/16 + 40px)}}.order{{margin:22px 0 0;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}.order button{{font:inherit;letter-spacing:inherit;text-transform:inherit;color:var(--muted);background:none;border:1px solid var(--rule);padding:6px 9px;margin-left:4px;cursor:pointer}}.order button[aria-pressed=true]{{color:var(--ink);border-color:var(--ink)}}li.current .poster{{outline:3px solid var(--accent);outline-offset:5px}}ol{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:28px 22px}}.poster{{display:block;box-shadow:0 10px 30px #251d1426;transition:transform .15s}}.poster:hover{{transform:translateY(-3px)}}.poster img{{display:block;width:100%;height:auto}}.caption{{display:flex;justify-content:space-between;gap:10px;margin:10px 2px 0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}.caption a{{font:11px var(--mono);letter-spacing:0;text-transform:none;color:var(--muted);text-decoration:none;white-space:nowrap}}.caption a:hover{{color:var(--accent)}}
@media print{{@page{{size:A4;margin:12mm}}body{{background:white}}header span{{text-align:left}}.slot,.screen,.order{{display:none!important}}.intro{{display:block;box-shadow:none;padding:0 0 8mm}}ol{{grid-template-columns:repeat(2,1fr);gap:8mm}}li{{break-inside:avoid}}.poster{{box-shadow:none;outline:1px solid #ddd}}li.current .poster{{outline:1px solid #ddd}}}}
@media(max-width:740px){{header{{padding:20px 16px 12px}}main{{padding:0 16px 30px}}.intro{{grid-template-columns:1fr;gap:24px;padding:26px 22px}}ol{{grid-template-columns:1fr}}}}
</style></head>
<body>
<header><strong><a href="../index.html">Field notes</a> · The quiet art</strong><span>Jefferson Fisher in conversation with Chris Williamson<br>Modern Wisdom · Published 4 May 2026 · 2h 11m</span></header>
<main>
<section class="intro"><div><div class="kicker">A poster wall · {len(rows)} posters</div><h1>The quiet art of<br><em>leading any conversation</em></h1><p class="deck">Advice from the conversation, set as posters and ordered by how well each line stands on its own. Every poster links to its moment in the video.</p><p class="order">Order <button data-order="score" aria-pressed="true">Best first</button><button data-order="time" aria-pressed="false">As spoken</button></p></div>
<div class="slot"><div class="screen"><div id="player"></div></div></div></section>
<ol>
{chr(10).join(cards)}
</ol>
</main>
<script>{PLAYER_SCRIPT}</script></body></html>
"""
(ROOT / "index.html").write_text(page)
print(f"Built index.html with {len(rows)} posters")
