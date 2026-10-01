"""Check a site's items against the transcript they were written from."""
from . import transcript as spoken


def problems(items, breaks, segments, ordered=True):
    found = []
    flat = []
    for segment in segments:
        flat += [(segment.start, w) for w in spoken.words(segment.text)]
    transcript_words = [w for _, w in flat]
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
            spoken_at = [flat[i][0] for i in occurrences(spoken.words(quote.text), transcript_words)]
            if not spoken_at:
                found.append(f"quote in {item.title!r} is not verbatim: {quote.text!r}")
                continue
            nearest = min(spoken_at, key=lambda t: abs(t - quote.start))
            if abs(nearest - quote.start) > QUOTE_DRIFT_S:
                found.append(f"quote in {item.title!r} is spoken at {nearest}s, not at {quote.start}s")
    return found


QUOTE_DRIFT_S = 60
CONVERSATION_EXCERPTS = {"Cold open"}


def occurrences(needle, haystack):
    if not needle:
        return []
    return [i for i, word in enumerate(haystack)
            if word == needle[0] and haystack[i:i + len(needle)] == needle]
