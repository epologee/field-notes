"""Check that the generated pages link every video site and its source moments."""
from pathlib import Path
import re
import subprocess
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parent.parent


def build(script):
    subprocess.run([sys.executable, str(script)], check=True, capture_output=True)


class IndexPage(unittest.TestCase):
    def test_lists_every_video_site(self):
        build(ROOT / "build.py")
        page = (ROOT / "index.html").read_text()
        for video in yaml.safe_load((ROOT / "videos.yaml").read_text())["videos"]:
            self.assertIn(f'href="{video["slug"]}/index.html"', page)
            self.assertTrue((ROOT / video["slug"] / "index.html").exists())


class RickRubinReading(unittest.TestCase):
    def setUp(self):
        build(ROOT / "rick-rubin" / "build.py")
        self.page = (ROOT / "rick-rubin" / "index.html").read_text()

    def test_links_back_to_the_index(self):
        self.assertIn('href="../index.html"', self.page)

    def test_title_page_embeds_the_video(self):
        self.assertIn('<div class="player"><div id="player"></div></div>', self.page)
        self.assertIn("const video='a_GiFiHXJ6g'", self.page)
        self.assertIn("https://www.youtube.com/iframe_api", self.page)

    def test_video_links_start_before_their_timestamp(self):
        lead = int(re.search(r"const lead=(\d+);", self.page).group(1))
        self.assertGreater(lead, 0)
        chapters = yaml.safe_load((ROOT / "rick-rubin" / "chapters.yaml").read_text())["chapters"]
        follow = next(c for c in chapters if c.get("continue_timestamp_s"))["continue_timestamp_s"]
        self.assertIn(f'?t={follow - lead}\\"', self.page)


if __name__ == "__main__":
    unittest.main()
