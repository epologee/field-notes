"""Site data shared by every reading site: the video entry, timecodes and breaks."""
from dataclasses import dataclass, field
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
LEAD_S = 2


def timecode(seconds):
    seconds = int(seconds)
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def check_label(label, seconds, what):
    if label != timecode(seconds):
        raise ValueError(f"{what}: label {label!r} disagrees with {seconds} seconds")
    return int(seconds)


def videos():
    return yaml.safe_load((ROOT / "videos.yaml").read_text())["videos"]


def video(slug):
    for entry in videos():
        if entry["slug"] == slug:
            return entry
    raise KeyError(f"{slug} is not in videos.yaml")


def published(entry):
    date = entry["published"]
    return f"{date.day} {date:%B %Y}"


@dataclass
class Break:
    kind: str
    label: str
    start: int
    end: int


def breaks(site_dir):
    path = Path(site_dir) / "breaks.yaml"
    if not path.exists():
        return []
    found = []
    for item in yaml.safe_load(path.read_text()).get("breaks") or []:
        start = check_label(item["start"], item["start_s"], f"break {item['kind']}")
        end = check_label(item["end"], item["end_s"], f"break {item['kind']}")
        if end <= start:
            raise ValueError(f"break {item['kind']} at {item['start']} ends before it starts")
        found.append(Break(item["kind"], item.get("label") or "", start, end))
    return sorted(found, key=lambda b: b.start)


@dataclass
class Quote:
    """Words attributed to a speaker. Verbatim words must match what was said; a paraphrase need not."""
    text: str
    start: int
    verbatim: bool = True


@dataclass
class Item:
    """One chapter or poster: where it starts in the video and what it quotes."""
    title: str
    start: int
    quotes: list = field(default_factory=list)
    content_note: str = ""


def read_chapters(path):
    """Chapters in the chapters.yaml form: title, timestamp, paragraphs, optional continue, quote and note."""
    found = []
    for chapter in yaml.safe_load(Path(path).read_text())["chapters"]:
        title = chapter["title"]
        if not isinstance(chapter.get("paragraphs"), list) or not chapter["paragraphs"]:
            raise ValueError(f"chapter {title!r} needs paragraphs")
        start = check_label(chapter["timestamp"], chapter["timestamp_s"], title)
        entry = {"title": title, "start": start, "paragraphs": chapter["paragraphs"]}
        if chapter.get("continue_timestamp_s") is not None:
            entry["continue"] = check_label(chapter["continue_timestamp"], chapter["continue_timestamp_s"], title)
        if chapter.get("quote"):
            entry["quote"] = chapter["quote"]
            entry["quote_start"] = int(chapter.get("quote_timestamp_s") or start)
        if chapter.get("content_note"):
            entry["content_note"] = chapter["content_note"]
        found.append(entry)
    return found


def chapter_items(chapters):
    return [Item(c["title"], c["start"], [Quote(c["quote"], c["quote_start"])] if "quote" in c else [],
                 c.get("content_note", "")) for c in chapters]


def chapter_prose(chapters):
    for chapter in chapters:
        for text in [chapter["title"], *chapter["paragraphs"], chapter.get("quote", "")]:
            yield chapter["title"], text
