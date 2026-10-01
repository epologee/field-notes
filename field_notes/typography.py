"""The typographic floor every site keeps: proper punctuation and recorded design research."""
from pathlib import Path
import re

PUNCTUATION = [
    (re.compile(r'"'), 'straight double quote, use “ ”'),
    (re.compile(r"'"), "straight single quote, use ‘ ’ or the apostrophe ’"),
    (re.compile(r"--"), "double hyphen, use a dash"),
    (re.compile(r"\s-\s"), "spaced hyphen, use a dash"),
    (re.compile(r"\.\.\."), "three dots, use the ellipsis …"),
    (re.compile(r"\S  +\S"), "double space"),
]
REQUIRED_TOKENS = ["--ink", "--paper", "--accent"]


def prose_problems(where, text):
    return [f"{where}: {why}: {text.strip()[:80]!r}" for pattern, why in PUNCTUATION if pattern.search(text)]


def design_problems(site_dir):
    readme = Path(site_dir) / "README.md"
    text = readme.read_text() if readme.exists() else ""
    section = re.search(r"^## Design\b.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not section:
        return [f"{readme}: no '## Design' section with the design research"]
    found = []
    if not re.search(r"#[0-9a-fA-F]{6}\b", section.group(1)):
        found.append(f"{readme}: the design section names no colour as a hex value")
    if not re.search(r"https?://", section.group(1)):
        found.append(f"{readme}: the design section lists no research source")
    return found


def token_problems(page):
    return [f"the page sets no {token} colour token" for token in REQUIRED_TOKENS if f"{token}:" not in page]
