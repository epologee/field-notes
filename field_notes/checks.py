"""Check a site's items against the transcript they were written from."""
import difflib

from . import transcript as spoken
from .transcript import CONVERSATION_EXCERPTS

QUOTE_DRIFT_S = 60
VERBATIM_RATIO = 0.85


def problems(items, breaks, segments, ordered=True):
    found = []
    flat = []
    for segment in segments:
        flat += [(segment.start, w) for w in spoken.words(segment.text)]
    starts = sorted(item.start for item in items)

    if ordered:
        for before, after in zip(items, items[1:]):
            if after.start < before.start:
                found.append(f"{after.title!r} starts before {before.title!r}")

    for item in items:
        for b in breaks:
            if b.kind not in CONVERSATION_EXCERPTS and b.start <= item.start < b.end:
                found.append(f"{item.title!r} starts at {item.start}s, inside the {b.kind.lower()} break")
        later = [s for s in starts if s > item.start]
        end = later[0] if later else float("inf")
        for quote in item.quotes:
            if not item.start <= quote.start < end:
                found.append(f"quote in {item.title!r} at {quote.start}s falls outside its item")
            if not quote.verbatim:
                continue
            likeness = closeness(spoken.words(quote.text), flat, quote.start)
            if likeness < VERBATIM_RATIO:
                found.append(f"quote in {item.title!r} matches what was said around {quote.start}s for only "
                             f"{likeness:.0%}; quote the words as spoken or present it as a paraphrase: {quote.text!r}")
    return found


def closeness(words, flat, near):
    """How closely the words match the best stretch of transcript spoken near a moment, from 0 to 1."""
    best = 0.0
    spoken_words = [w for _, w in flat]
    for i, (start, _) in enumerate(flat):
        if abs(start - near) > QUOTE_DRIFT_S:
            continue
        match = difflib.SequenceMatcher(None, words, spoken_words[i:i + len(words)], autojunk=False)
        if match.quick_ratio() > best:
            best = max(best, match.ratio())
    return best
