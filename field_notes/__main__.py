"""python3 -m field_notes build | check | index | breaks | new"""
import argparse
import importlib.util
import json
import sys

from . import breaks as ad_breaks, checks, site_index, transcript, typography
from .episode import ROOT, breaks, video, videos

NEW_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<!-- field-notes:head -->
<style>:root{--ink:#000000;--paper:#ffffff;--accent:#000000}</style>
</head>
<body>
<header><a href="../index.html">Field notes</a> · <!-- field-notes:published --></header>
<main id="pages"><div id="player"></div></main>
<!-- field-notes:runtime -->
<script>
</script>
</body></html>
"""
NEW_README = """# {speaker}: {title}

## Design

Theme, every colour as a hex value with its reason, the type, and the research sources as links.
"""


def site(slug):
    path = ROOT / slug / "build.py"
    spec = importlib.util.spec_from_file_location(f"site_{slug.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(slug=None):
    for entry in videos():
        if slug in (None, entry["slug"]):
            print(site(entry["slug"]).build())
    print(f"Built index.html with {site_index.build()} videos")


def check(slug, transcript_path):
    module = site(slug)
    items = module.items()
    found = checks.problems(items, breaks(ROOT / slug), transcript.read(transcript_path),
                            ordered=getattr(module, "ORDERED", True))
    for where, text in module.prose():
        found += typography.prose_problems(where, text)
    found += typography.design_problems(ROOT / slug)
    for problem in found:
        print(problem)
    print(f"{slug}: {len(found)} problems")
    return 1 if found else 0


def index(slug, transcript_path):
    item_starts = sorted({item.start for item in site(slug).items()})
    found = transcript.index(transcript.read(transcript_path), breaks(ROOT / slug), item_starts)
    path = ROOT / slug / "transcript-index.json"
    path.write_text(json.dumps(found, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Wrote {path.relative_to(ROOT)} with {len(found['windows'])} windows")


def fetch_breaks(slug, overwrite):
    path = ROOT / slug / "breaks.yaml"
    if path.exists() and not overwrite:
        sys.exit(f"{path.relative_to(ROOT)} exists; pass --overwrite to replace its hand-written labels")
    ad_breaks.write(ROOT / slug, video(slug)["youtube_id"])
    print(f"Wrote {path.relative_to(ROOT)}")


def new(slug):
    entry = video(slug)
    folder = ROOT / slug
    folder.mkdir(exist_ok=False)
    (folder / "template.html").write_text(NEW_TEMPLATE)
    (folder / "README.md").write_text(NEW_README.format(**entry))
    print(f"Created {slug}/ with template.html and README.md; add build.py next")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m field_notes")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build").add_argument("slug", nargs="?")
    for name in ("check", "index"):
        command = commands.add_parser(name)
        command.add_argument("slug")
        command.add_argument("--transcript", required=True)
    command = commands.add_parser("breaks")
    command.add_argument("slug")
    command.add_argument("--overwrite", action="store_true")
    commands.add_parser("new").add_argument("slug")
    args = parser.parse_args(argv)
    if args.command == "build":
        return build(args.slug)
    if args.command == "check":
        return check(args.slug, args.transcript)
    if args.command == "index":
        return index(args.slug, args.transcript)
    if args.command == "breaks":
        return fetch_breaks(args.slug, args.overwrite)
    return new(args.slug)


sys.exit(main())
