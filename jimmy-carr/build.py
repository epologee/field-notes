#!/usr/bin/env python3
"""Build the Jimmy Carr reading page from chapters.yaml and template.html."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from field_notes import render  # noqa: E402
from field_notes.episode import LEAD_S, breaks, chapter_items, chapter_prose, read_chapters  # noqa: E402

SLUG = "jimmy-carr"
TITLE = "Jimmy Carr: We’re at the Beginning of a Revolution"
DESCRIPTION = "Jimmy Carr in conversation with Chris Williamson, read as forty-nine short chapters with direct links into the moments that matter."
CONTENT_NOTE = "Jimmy Carr describes how he talks about suicide in his show. It is his view, not clinical advice."


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
        "speaker": "Jimmy Carr",
        "chapterLabel": "",
        "contentGroup": "In the set list",
        "contentNote": CONTENT_NOTE,
        "chapters": found,
        "breaks": [vars(b) for b in breaks(HERE)],
        "transcript": json.loads(index.read_text()) if index.exists() else [],
    }
    render.write(SLUG, render.page((HERE / "template.html").read_text(), SLUG, TITLE, DESCRIPTION, data))
    return f"Built {SLUG}/index.html with {len(found)} chapters"


if __name__ == "__main__":
    print(build())
