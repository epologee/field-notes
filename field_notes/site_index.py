"""Build the index page that lists every video reading site from videos.yaml."""
import html

from .episode import ROOT, published, videos as all_videos

def entry(video):
    if not (ROOT / video["slug"] / "index.html").exists():
        raise SystemExit(f"{video['slug']}/index.html is missing")
    e = {k: html.escape(str(v)) for k, v in video.items()}
    e["published"] = published(video)
    return f"""<li><a class="entry" href="{e['slug']}/index.html">
<img src="https://i.ytimg.com/vi/{e['youtube_id']}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">
<div><p class="meta">{e['show']} · Published {e['published']} · {e['duration']}</p>
<h2>{e['speaker']}<br><em>{e['title']}</em></h2>
<p class="summary">{e['summary']}</p>
<p class="with">In conversation with {e['host']} · {e['contents']}</p></div></a>
<a class="source" href="https://www.youtube.com/watch?v={e['youtube_id']}" target="_blank" rel="noopener">Watch on YouTube ↗</a></li>"""

def build():
    videos = sorted(all_videos(), key=lambda v: str(v["added"]), reverse=True)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Field notes</title>
<meta name="description" content="Close readings of long conversations on YouTube, with direct links into the moments that matter.">
<meta property="og:type" content="website"><meta property="og:site_name" content="Field notes"><meta property="og:title" content="Field notes">
<meta property="og:description" content="Close readings of long conversations on YouTube, with direct links into the moments that matter.">
<meta property="og:url" content="https://epologee.github.io/field-notes/"><meta name="twitter:card" content="summary">
<style>
:root{{--ink:#211d19;--muted:#766e63;--paper:#f7f3eb;--desk:#d9d1c4;--rule:#cfc6b8;--accent:#a84f32;--serif:"Iowan Old Style",Baskerville,Georgia,serif;--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}*{{box-sizing:border-box}}body{{margin:0;background:var(--desk);color:var(--ink);font:16px/1.55 var(--sans)}}main{{max-width:880px;margin:auto;padding:30px 28px 50px}}header{{padding:40px 0 34px}}.kicker,.meta,.with{{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}h1{{font:500 clamp(48px,8vw,80px)/.98 var(--serif);letter-spacing:-.045em;margin:18px 0 16px}}.deck{{font:20px/1.45 var(--serif);max-width:560px;color:#554c42;margin:0}}ol{{list-style:none;padding:0;margin:0;display:grid;gap:22px}}li{{background:var(--paper);box-shadow:0 10px 34px #251d141c}}.entry{{display:grid;grid-template-columns:260px 1fr;gap:28px;padding:28px;color:inherit;text-decoration:none}}.entry img{{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block;filter:saturate(.85)}}.meta{{color:var(--accent);margin:0}}h2{{font:500 clamp(30px,4.5vw,42px)/1.03 var(--serif);letter-spacing:-.03em;margin:12px 0 12px}}h2 em{{color:var(--accent);font-weight:400}}.entry:hover h2{{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:5px}}.summary{{font:17px/1.55 var(--serif);color:#39332d;margin:0 0 14px}}.with{{margin:0}}.source{{display:block;border-top:1px solid var(--rule);margin:0 28px;padding:11px 0 14px;font-size:11px;color:var(--muted);text-decoration:none;text-align:right}}.source:hover{{color:var(--accent)}}
@media(max-width:640px){{main{{padding:16px 16px 36px}}header{{padding:24px 0 24px}}.entry{{grid-template-columns:1fr;gap:18px;padding:20px}}.source{{margin:0 20px}}}}
</style></head>
<body><main>
<header><div class="kicker">Field notes · {len(videos)} {"conversation" if len(videos) == 1 else "conversations"}</div><h1>Field notes</h1><p class="deck">Close readings of long conversations on YouTube, with direct links into the moments that matter.</p></header>
<ol>
{chr(10).join(entry(v) for v in videos)}
</ol>
</main></body></html>
"""
    (ROOT / "index.html").write_text(page)
    return len(videos)
