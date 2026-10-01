"""Read a timecoded transcript and turn it into the word index that a page may publish.

The index holds, per window of WINDOW_S seconds, the distinct words spoken in it,
sorted alphabetically and without stopwords, so search can find a moment without
the page carrying the transcript itself.
"""
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

WINDOW_S = 30
LINE = re.compile(r"^\[(\d+):(\d\d):(\d\d)\]\s*(?:\*\*[^*]+:\*\*\s*)?(.*)$")
WORD = re.compile(r"[^\W_]+")
STOPWORDS = set("""
a about above after again all also am an and any are as at be because been before being but by can could
did do does doing don down during each even few for from further get got had has have having he her here
hers him his how i if in into is it its just know like me more most my no nor not now of off oh on once
only or other our ours out over own really right s same she should so some such t than that the their them
then there these they this those through to too um uh under until up us very was we were what when where
which while who whom why will with would yeah yes you your yours ll re ve d m
""".split())


@dataclass
class Segment:
    start: int
    text: str


def words(text):
    stripped = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))
    return WORD.findall(stripped)


def read(path):
    segments = []
    for line in Path(path).read_text().splitlines():
        match = LINE.match(line.strip())
        if match and match.group(4).strip():
            h, m, s, text = match.groups()
            segments.append(Segment(int(h) * 3600 + int(m) * 60 + int(s), text.strip()))
    if not segments:
        raise ValueError(f"{path} has no timecoded lines")
    return segments


def index(segments):
    windows = {}
    for segment in segments:
        bucket = segment.start // WINDOW_S * WINDOW_S
        windows.setdefault(bucket, set()).update(w for w in words(segment.text) if w not in STOPWORDS)
    return [[start, " ".join(sorted(found))] for start, found in sorted(windows.items()) if found]
