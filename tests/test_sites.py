"""Every site builds from the shared library and keeps its own data promises."""
from pathlib import Path
import csv
import json
import re
import subprocess
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SITES = ["rick-rubin", "jefferson-fisher", "jimmy-carr"]


def setUpModule():
    subprocess.run([sys.executable, "-m", "field_notes", "build"], cwd=ROOT, check=True, capture_output=True)


def page(slug):
    return (ROOT / slug / "index.html").read_text()


def data(slug):
    return json.loads(re.search(r"const FIELD_NOTES=(.*?);\n</script>", page(slug), re.S).group(1).replace("<\\/", "</"))


class EverySite(unittest.TestCase):
    def test_index_lists_every_site_with_its_publication_date(self):
        index = (ROOT / "index.html").read_text()
        for video in yaml.safe_load((ROOT / "videos.yaml").read_text())["videos"]:
            self.assertIn(f'href="{video["slug"]}/index.html"', index)
            date = video["published"]
            self.assertIn(f"Published {date.day} {date:%B %Y}", index)
            self.assertIn(f"Published {date.day} {date:%B %Y}", page(video["slug"]))

    def test_each_page_carries_the_library_its_data_and_share_metadata(self):
        for slug in SITES:
            with self.subTest(slug):
                html = page(slug)
                self.assertIn('href="../index.html"', html)
                self.assertIn("FieldNotes.mount(", html)
                self.assertIn('<div id="player"></div>', html)
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
                self.assertNotIn("field-notes:", html.split("<script>")[0].replace('content="Field notes"', ""))
                entry = next(v for v in yaml.safe_load((ROOT / "videos.yaml").read_text())["videos"] if v["slug"] == slug)
                self.assertEqual(data(slug)["video"], entry["youtube_id"])

    def test_every_page_links_the_field_notes_icons(self):
        for path, prefix in [(ROOT / "index.html", ""), *[(ROOT / slug / "index.html", "../") for slug in SITES]]:
            with self.subTest(path.parent.name):
                html = path.read_text()
                for icon in ("favicon.svg", "favicon-32.png", "apple-touch-icon.png"):
                    self.assertIn(f'href="{prefix}{icon}"', html)
                    self.assertTrue((ROOT / icon).exists(), icon)

    def test_the_transcript_is_published_only_as_a_word_index(self):
        for slug in SITES:
            with self.subTest(slug):
                windows = data(slug)["transcript"]["windows"]
                self.assertTrue(windows)
                item_starts = {c["start"] for c in data(slug).get("chapters", [])} | {
                    int(s) for s in re.findall(r'data-seconds="(\d+)"', page(slug))}
                for start, words in windows:
                    listed = words.split(" ")
                    self.assertEqual(listed, sorted(set(listed)))
                    self.assertTrue(start % 30 == 0 or start in item_starts, start)
                self.assertEqual([s for s, _ in windows], sorted({s for s, _ in windows}))

    def test_every_site_knows_its_breaks(self):
        for slug in SITES:
            with self.subTest(slug):
                self.assertTrue(data(slug)["breaks"])
                self.assertTrue(all(b["label"] for b in data(slug)["breaks"]))


class ChapterSites(unittest.TestCase):
    def test_every_chapter_title_and_quote_reaches_the_page(self):
        for slug in ["rick-rubin", "jimmy-carr"]:
            source = yaml.safe_load((ROOT / slug / "chapters.yaml").read_text())["chapters"]
            chapters = data(slug)["chapters"]
            self.assertEqual([c["title"] for c in chapters], [c["title"] for c in source])
            self.assertEqual([c.get("quote") for c in chapters], [c.get("quote") for c in source])



class PosterWall(unittest.TestCase):
    def test_every_quote_becomes_a_poster_on_the_wall(self):
        with (ROOT / "jefferson-fisher" / "wisdom.csv").open() as source:
            quotes = len(list(csv.DictReader(source)))
        posters = re.findall(r'<img src="(posters/[^"]+\.svg)"', page("jefferson-fisher"))
        self.assertEqual(len(posters), quotes)
        self.assertEqual(len(data("jefferson-fisher")["docs"]), quotes)
        for path in posters:
            self.assertTrue((ROOT / "jefferson-fisher" / path).exists(), path)

    def test_a_paraphrased_poster_says_so(self):
        with (ROOT / "jefferson-fisher" / "wisdom.csv").open() as source:
            rows = list(csv.DictReader(source))
        self.assertTrue({r["wording"] for r in rows} <= {"verbatim", "paraphrase"})
        for row in rows[:20]:
            svg = (ROOT / "jefferson-fisher" / "posters" / f"{row['timestamp_s']}.svg")
            if svg.exists():
                self.assertEqual("Paraphrasing" in svg.read_text(), row["wording"] == "paraphrase", row["quote"])

    def test_poster_links_keep_their_address(self):
        self.assertIn('<li id="p3721" data-seconds="3721"><a class="poster" href="#p3721">', page("jefferson-fisher"))


if __name__ == "__main__":
    unittest.main()
