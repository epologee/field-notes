#!/usr/bin/env python3
"""Build the standalone reading page from chapters.yaml."""
from pathlib import Path
import html
import json
import re
import yaml

ROOT = Path(__file__).resolve().parent
DATA = yaml.safe_load((ROOT / "chapters.yaml").read_text())
VIDEO = DATA["video"].split("?", 1)[0]
chapters = DATA["chapters"]
# Links start a little before the transcript timestamp, so the first word is not clipped.
LEAD_S = 2

def timecode(seconds):
    seconds = int(seconds)
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"

rows = []
for chapter in chapters:
    paragraphs = chapter["paragraphs"]
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError(f"chapter {chapter.get('title')!r} needs paragraphs")
    start = int(chapter["timestamp_s"])
    if chapter.get("timestamp") != timecode(start):
        raise ValueError(f"timestamp label disagrees with timestamp_s for {chapter['title']!r}")
    extra = paragraphs[1] if len(paragraphs) > 1 else ""
    if chapter.get("continue_timestamp_s") is not None:
        follow = int(chapter["continue_timestamp_s"])
        if chapter.get("continue_timestamp") != timecode(follow):
            raise ValueError(f"continue timestamp label disagrees with seconds for {chapter['title']!r}")
        extra += f' <a class="time" href="{VIDEO}?t={max(0, follow - LEAD_S)}" target="_blank" rel="noopener">Continue at {timecode(follow)} ↗</a>'
    rows.append([timecode(start), html.escape(chapter["title"]), start,
                 html.escape(paragraphs[0]), extra,
                 html.escape(chapter["quote"]) if chapter.get("quote") else None,
                 chapter.get("quote_timestamp_s"), html.escape(chapter["content_note"]) if chapter.get("content_note") else None])

page = (ROOT / "index.html").read_text()
page = re.sub(r"const lead=\d+;", f"const lead={LEAD_S};", page)
pattern = r"const entries=.*?;\nconst toc="
replacement = "const entries=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\nconst toc="
updated, count = re.subn(pattern, lambda _: replacement, page, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not find generated chapter-data block in index.html")
(ROOT / "index.html").write_text(updated)
print(f"Built index.html with {len(rows)} chapters")
