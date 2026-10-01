#!/usr/bin/env python3
"""Build the Rick Rubin reading page from chapters.yaml and template.html."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from field_notes import render  # noqa: E402
from field_notes.episode import LEAD_S, breaks, chapter_items, chapter_prose, read_chapters  # noqa: E402

SLUG = "rick-rubin"
TITLE = "Rick Rubin: The Creative Act"
DESCRIPTION = "A close, thematic reading of Rick Rubin in conversation with Steven Bartlett, with direct links into the moments that matter."
CONTENT_NOTE = "This chapter recounts Rick Rubin’s personal experience, not a clinical explanation or advice."


def chapters():
    return read_chapters(HERE / "chapters.yaml")


def items():
    return chapter_items(chapters())


def prose():
    return chapter_prose(chapters())


def build():
    index = HERE / "transcript-index.json"
    found = chapters()
    data = {
        "lead": LEAD_S,
        "speaker": "Rick Rubin",
        "chapterLabel": "Chapter ",
        "contentGroup": "In the chapters",
        "contentNote": CONTENT_NOTE,
        "chapters": found,
        "breaks": [vars(b) for b in breaks(HERE)],
        "transcript": json.loads(index.read_text()) if index.exists() else {},
    }
    render.write(SLUG, render.page((HERE / "template.html").read_text(), SLUG, TITLE, DESCRIPTION, data))
    return f"Built {SLUG}/index.html with {len(found)} chapters"


if __name__ == "__main__":
    print(build())
