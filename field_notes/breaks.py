"""Find the stretches of a video that are not conversation, using SponsorBlock.

https://wiki.sponsor.ajay.app/w/API_Docs describes the skipSegments endpoint.
Overlapping and touching segments merge into one break, named after the category
that covers most of it. The result is written to breaks.yaml, where labels are
filled in by hand.
"""
from pathlib import Path
import json
import urllib.error
import urllib.parse
import urllib.request

from .episode import timecode

API = "https://sponsor.ajay.app/api/skipSegments"
KINDS = {
    "preview": "Cold open",
    "intro": "Cold open",
    "sponsor": "Sponsors",
    "selfpromo": "Promotion",
    "interaction": "Promotion",
    "outro": "Outro",
}
TOUCHING_S = 5


def fetch(youtube_id):
    query = urllib.parse.urlencode({"videoID": youtube_id, "categories": json.dumps(list(KINDS))})
    try:
        with urllib.request.urlopen(f"{API}?{query}", timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return []
        raise


def merge(segments):
    groups = []
    for segment in sorted(segments, key=lambda s: s["segment"][0]):
        start, end = segment["segment"]
        covered = {segment["category"]: end - start}
        if groups and start <= groups[-1]["end"] + TOUCHING_S:
            group = groups[-1]
            group["end"] = max(group["end"], end)
            for category, length in covered.items():
                group["covered"][category] = group["covered"].get(category, 0) + length
        else:
            groups.append({"start": start, "end": end, "covered": covered})
    return [{"kind": KINDS[max(g["covered"], key=g["covered"].get)],
             "start_s": int(g["start"]), "end_s": int(round(g["end"]))} for g in groups]


def to_yaml(found):
    lines = ["breaks:"]
    for b in found:
        lines += [f"- kind: {b['kind']}", f"  label: {b.get('label', '')}",
                  f"  start: {timecode(b['start_s'])}", f"  start_s: {b['start_s']}",
                  f"  end: {timecode(b['end_s'])}", f"  end_s: {b['end_s']}"]
    return "\n".join(lines) + "\n"


def write(site_dir, youtube_id):
    path = Path(site_dir) / "breaks.yaml"
    path.write_text(to_yaml(merge(fetch(youtube_id))))
    return path
