"""Fill a site template: shared head, publication date, runtime and site data."""
from pathlib import Path
import html
import json

from . import typography
from .episode import ROOT, published, video

HERE = Path(__file__).resolve().parent
SITE_URL = "https://epologee.github.io/field-notes"
HEAD = "<!-- field-notes:head -->"
PUBLISHED = "<!-- field-notes:published -->"
RUNTIME = "<!-- field-notes:runtime -->"


def head(slug, title, description):
    entry = video(slug)
    e = {k: html.escape(str(v)) for k, v in entry.items()}
    title, description = html.escape(title), html.escape(description)
    return f"""<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Field notes">
<meta property="og:title" content="{title}"><meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE_URL}/{slug}/index.html"><meta property="og:image" content="https://i.ytimg.com/vi/{e['youtube_id']}/maxresdefault.jpg">
<meta property="og:image:width" content="1280"><meta property="og:image:height" content="720"><meta property="og:image:alt" content="{e['speaker']} and {e['host']} on {e['show']}">
<meta name="twitter:card" content="summary_large_image">
<style>{(HERE / 'base.css').read_text().strip()}</style>"""


def runtime(data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"<script>\n{(HERE / 'runtime' / 'field-notes.js').read_text().strip()}\nconst FIELD_NOTES={payload};\n</script>"


def page(template, slug, title, description, data):
    for marker in (HEAD, RUNTIME):
        if template.count(marker) != 1:
            raise ValueError(f"{slug}: the template needs exactly one {marker}")
    entry = video(slug)
    data = {"video": entry["youtube_id"], **data}
    filled = (template.replace(HEAD, head(slug, title, description))
              .replace(PUBLISHED, f"Published {published(entry)}")
              .replace(RUNTIME, runtime(data)))
    problems = typography.token_problems(filled)
    if problems:
        raise ValueError(f"{slug}: " + "; ".join(problems))
    return filled


def write(slug, html_text):
    (ROOT / slug / "index.html").write_text(html_text)
