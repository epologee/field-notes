#!/usr/bin/env python3
"""Render a wisdom-CSV row as a poster SVG.

Examples:
  ./poster.py 3721 --lines "The conversation|you're avoiding|is the result|you're choosing." --accent "avoiding,choosing"
  ./poster.py 5552
"""
from __future__ import annotations
import argparse, csv, pathlib, re, sys, html, textwrap

try:
    from contexts import CONTEXTS
except ImportError:
    CONTEXTS = {}

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from field_notes.episode import published, video  # noqa: E402

EPISODE = video("jefferson-fisher")
EPISODE_TITLE = "The Quiet Art of Leading Any Conversation"
EPISODE_DATE = published(EPISODE)
SHOW = EPISODE["show"]
HOST = EPISODE["host"]
VIDEO_ID = EPISODE["youtube_id"]

CSV_PATH = pathlib.Path(__file__).parent / "wisdom.csv"
OUT_DIR = pathlib.Path(__file__).parent / "posters"

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1350" preserveAspectRatio="xMidYMid meet">
  <defs>
    <style>
      .stage    {{ fill: #ffffff; }}
      .rule     {{ stroke: #0e0e0e; stroke-width: 1.1; }}
      .eyebrow  {{ font-family: "Inter", "Helvetica Neue", system-ui, sans-serif;
                  font-size: 15px; letter-spacing: 0.24em; text-transform: uppercase;
                  fill: #0e0e0e; font-weight: 600; }}
      .show     {{ font-family: "Inter", "Helvetica Neue", system-ui, sans-serif;
                  font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase;
                  fill: #6b6b6b; font-weight: 500; }}
      .quote    {{ font-family: "EB Garamond", "Sorts Mill Goudy", "Apple Garamond", Garamond, "Times New Roman", serif;
                  fill: #0e0e0e; font-weight: 500; }}
      .display  {{ font-size: {fontsize}px; line-height: 1.04; letter-spacing: -0.012em; }}
      .accent   {{ font-style: italic; font-weight: 500; fill: #b14a2a; }}
      .attrib   {{ font-family: "Inter", "Helvetica Neue", system-ui, sans-serif;
                  font-size: 17px; letter-spacing: 0.18em; text-transform: uppercase;
                  fill: #0e0e0e; font-weight: 600; }}
      .small    {{ font-family: "Inter", "Helvetica Neue", system-ui, sans-serif;
                  font-size: 13px; letter-spacing: 0.14em; text-transform: uppercase;
                  fill: #6b6b6b; font-weight: 400; }}
      .urltext  {{ font-family: "JetBrains Mono", "SF Mono", ui-monospace, Menlo, monospace;
                  font-size: 12px; letter-spacing: 0.02em;
                  fill: #6b6b6b; font-weight: 400; }}
      .context  {{ font-family: "EB Garamond", "Sorts Mill Goudy", "Apple Garamond", Garamond, "Times New Roman", serif;
                  font-size: 22px; line-height: 1.42; fill: #3a3a3a;
                  font-style: italic; font-weight: 400; }}
    </style>
  </defs>

  <rect class="stage" width="1080" height="1350"/>

  <g transform="translate(96 96)">
    <text class="show"    y="0">{show} · hosted by {host}</text>
    <text class="eyebrow" y="34">{episode}</text>
    <line class="rule" x1="0" y1="58" x2="888" y2="58"/>
  </g>

  <g transform="translate(96 {quote_y})">
    <text class="quote display" x="0" y="0">
{tspans}
    </text>
  </g>

{context_block}

  <g transform="translate(96 1196)">
    <line class="rule" x1="0" y1="0" x2="888" y2="0"/>
    <text class="attrib" x="0" y="38">{attrib}</text>
    <text class="small"  x="0" y="68">{show} · {episode_date} · {timecode}</text>
    <a href="https://youtu.be/{video_id}?t={timestamp_s}" target="_blank" rel="noopener">
      <text class="urltext" x="888" y="68" text-anchor="end">youtu.be/{video_id}?t={timestamp_s}</text>
    </a>
  </g>
</svg>
"""

def apply_accents(line: str, accents: list[str]) -> str:
    """Wrap accent words in <tspan class='accent'>...</tspan>, preserving boundaries.

    We escape first, then re-insert tspan markup so SVG XML is well-formed.
    """
    out = html.escape(line, quote=False)
    for word in accents:
        if not word:
            continue
        # Word-ish boundary, case-insensitive, preserve original case.
        pattern = re.compile(rf"(?<!\w)({re.escape(word)})(?!\w)", re.IGNORECASE)
        out = pattern.sub(r'<tspan class="accent">\1</tspan>', out)
    return out

AVERAGE_GLYPH_WIDTH_EM = 0.48
CONTEXT_LAST_BASELINE = 1150

def pick_fontsize(lines: list[str], height: int = 10_000) -> int:
    """Largest display size at which every line fits 888px and the block fits the height."""
    longest = max(len(l) for l in lines)
    return int(min(138, 888 / (longest * AVERAGE_GLYPH_WIDTH_EM), height / (len(lines) * 1.04)))

def fit_lines(quote: str, height: int) -> list[str]:
    """Break the quote at the width that allows the largest type within the quote area."""
    options = [textwrap.wrap(quote, width) for width in range(8, 60)]
    return max(options, key=lambda lines: (pick_fontsize(lines, height), -len(lines)))

def pick_quote_y(n_lines: int, fontsize: int, reserve_bottom: int = 0) -> int:
    """Visually center the block between the top rule and the reserved-bottom area."""
    block_height = n_lines * fontsize * 1.04
    available_top = 200
    available_bottom = 1180 - reserve_bottom
    center = (available_top + available_bottom) // 2
    return int(center - block_height / 2 + fontsize * 0.78)

def render_context(text: str, quote_y: int, quote_lines: int, quote_fontsize: int) -> str:
    """Render the context paragraph as a wrapped italic-serif block below the quote."""
    if not text:
        return ""
    wrapped = textwrap.wrap(text, width=64)
    ctx_y = int(CONTEXT_LAST_BASELINE - (len(wrapped) - 1) * 22 * 1.42)
    line_height_em = 1.42
    tspans = []
    for i, line in enumerate(wrapped):
        dy = "0" if i == 0 else f"{line_height_em}em"
        tspans.append(f'      <tspan x="0" dy="{dy}">{html.escape(line)}</tspan>')
    return (
        f'  <g transform="translate(96 {ctx_y})">\n'
        f'    <text class="context" x="0" y="0">\n'
        + "\n".join(tspans) + "\n"
        f'    </text>\n'
        f'  </g>'
    )

def timecode(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def find_row(timestamp_s: int) -> dict[str, str]:
    for row in csv.DictReader(CSV_PATH.open()):
        if int(row["timestamp_s"]) == timestamp_s:
            return row
    sys.exit(f"no row with timestamp_s={timestamp_s} in {CSV_PATH}")

def context_for(row: dict[str, str]) -> str:
    return CONTEXTS.get(int(row["timestamp_s"]), row.get("context", ""))

def attribution(row: dict[str, str]) -> str:
    """A paraphrased line must not read as words the speaker said."""
    name = row["attributed_to"]
    return name if row.get("wording", "verbatim") == "verbatim" else f"Paraphrasing {name}"

def curl_quotes(text: str) -> str:
    text = re.sub(r"(^|[\s(])'", "\\1\u2018", text)
    return text.replace("'", "\u2019")

def render(row: dict[str, str], lines: list[str] | None = None, accents: list[str] = (), with_context: bool = True) -> str:
    """Return the poster SVG for one wisdom-CSV row."""
    timestamp_s = int(row["timestamp_s"])
    ctx_text = curl_quotes(context_for(row)) if with_context else ""
    if ctx_text:
        wrapped_lines = max(1, len(textwrap.wrap(ctx_text, width=64)))
        ctx_reserve = 80 + int(wrapped_lines * 22 * 1.42) + 40
    else:
        ctx_reserve = 0
    quote_height = 1180 - ctx_reserve - 200 - 40
    lines = [curl_quotes(line) for line in lines or fit_lines(row["quote"], quote_height)]
    fontsize = pick_fontsize(lines, quote_height)
    quote_y = pick_quote_y(len(lines), fontsize, reserve_bottom=ctx_reserve)
    context_block = render_context(ctx_text, quote_y, len(lines), fontsize)

    tspans = []
    for i, line in enumerate(lines):
        marked = apply_accents(line, list(accents))
        dy = "0" if i == 0 else "1.04em"
        tspans.append(f'      <tspan x="0" dy="{dy}">{marked}</tspan>')

    return TEMPLATE.format(
        show=html.escape(SHOW),
        host=html.escape(HOST),
        episode=html.escape(EPISODE_TITLE),
        episode_date=html.escape(EPISODE_DATE),
        fontsize=fontsize,
        quote_y=quote_y,
        tspans="\n".join(tspans),
        context_block=context_block,
        attrib=html.escape(attribution(row)),
        timecode=timecode(timestamp_s),
        video_id=VIDEO_ID,
        timestamp_s=timestamp_s,
    )

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("timestamp_s", type=int, help="row to render, by timestamp_s value")
    p.add_argument("--lines", default=None, help="quote split by '|'; default: heuristic split")
    p.add_argument("--accent", default="", help="comma-separated words to italic-accent")
    p.add_argument("--out", default=None, help="output path; default: posters/<timestamp>.svg")
    p.add_argument("--no-context", action="store_true", help="omit the context paragraph below the quote")
    args = p.parse_args()

    row = find_row(args.timestamp_s)
    lines = args.lines.split("|") if args.lines else None
    accents = [a.strip() for a in args.accent.split(",") if a.strip()]
    out = render(row, lines, accents, with_context=not args.no_context)

    OUT_DIR.mkdir(exist_ok=True)
    out_path = pathlib.Path(args.out) if args.out else OUT_DIR / f"{args.timestamp_s}.svg"
    out_path.write_text(out)
    print(out_path)

if __name__ == "__main__":
    main()
