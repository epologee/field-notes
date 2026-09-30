"""Check that the generated pages link every video site and its source moments."""
from pathlib import Path
import html
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
        self.assertIn('<div class="screen"><div id="player"></div></div>', self.page)
        self.assertIn("const video='a_GiFiHXJ6g'", self.page)
        self.assertIn("https://www.youtube.com/iframe_api", self.page)

    def test_chapters_follow_the_playing_video(self):
        self.assertIn("follow=setInterval(followVideo,1000)", self.page)
        self.assertIn("if(started&&!fromVideo)seekChapter(active);", self.page)
        self.assertIn("if(pending){", self.page)
        self.assertIn("else if(lastT>30&&t<5){hold=", self.page)
        self.assertIn("player.cueVideoById({videoId:video,startSeconds:", self.page)

    def test_player_is_available_on_every_chapter(self):
        self.assertIn(".reading .screen{display:block;position:fixed", self.page)
        self.assertNotIn(".reading .screen{display:none}", self.page)

    def test_menu_leads_back_to_the_title_page(self):
        self.assertIn('<a id="cover-link" href="#"><i>00</i>Title page</a>', self.page)
        self.assertIn("function showCover()", self.page)

    def test_video_stays_out_of_print(self):
        self.assertIn(".toc,header,.cover,.nav,.note,.screen{display:none!important}", self.page)

    def test_share_preview_shows_the_video_thumbnail(self):
        self.assertIn('<meta property="og:image" content="https://i.ytimg.com/vi/a_GiFiHXJ6g/maxresdefault.jpg">', self.page)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', self.page)

    def test_video_links_start_before_their_timestamp(self):
        lead = int(re.search(r"const lead=(\d+);", self.page).group(1))
        self.assertGreater(lead, 0)
        chapters = yaml.safe_load((ROOT / "rick-rubin" / "chapters.yaml").read_text())["chapters"]
        follow = next(c for c in chapters if c.get("continue_timestamp_s"))["continue_timestamp_s"]
        self.assertIn(f'?t={follow - lead}\\"', self.page)



class JeffersonFisherPosterWall(unittest.TestCase):
    def setUp(self):
        build(ROOT / "jefferson-fisher" / "build.py")
        self.page = (ROOT / "jefferson-fisher" / "index.html").read_text()

    def test_every_quote_becomes_a_poster_on_the_wall(self):
        with (ROOT / "jefferson-fisher" / "wisdom.csv").open() as source:
            quotes = len(source.readlines()) - 1
        posters = re.findall(r'<img src="(posters/[^"]+\.svg)"', self.page)
        self.assertEqual(len(posters), quotes)
        for path in posters:
            self.assertTrue((ROOT / "jefferson-fisher" / path).exists(), path)

    def test_links_back_to_the_index(self):
        self.assertIn('href="../index.html"', self.page)

    def test_wall_follows_the_playing_video_in_a_docked_player(self):
        self.assertIn(".docked .screen{position:fixed", self.page)
        self.assertIn("following=setInterval(follow,1000)", self.page)
        self.assertIn("order('time')", self.page)

    def test_video_stays_out_of_print(self):
        self.assertIn(".slot,.screen,.order{display:none!important}", self.page)

    def test_poster_links_land_on_the_wall_with_the_player(self):
        self.assertIn('<li id="p3721" data-seconds="3721"><a class="poster" href="#p3721">', self.page)
        self.assertIn("!entries.at(-1).isIntersecting", self.page)
        self.assertIn("player.cueVideoById({videoId:video,startSeconds:to})", self.page)



class JimmyCarrReading(unittest.TestCase):
    def setUp(self):
        build(ROOT / "jimmy-carr" / "build.py")
        self.page = (ROOT / "jimmy-carr" / "index.html").read_text()
        self.chapters = yaml.safe_load((ROOT / "jimmy-carr" / "chapters.yaml").read_text())["chapters"]

    def test_every_chapter_links_into_the_video_with_a_quote(self):
        for chapter in self.chapters:
            self.assertTrue(chapter["quote"])
            self.assertIn(html.escape(chapter["title"]), self.page)
        self.assertIn("const video='gAxNYd01I6E'", self.page)

    def test_player_follows_the_chapters(self):
        self.assertIn("follow=setInterval(followVideo,1000)", self.page)
        self.assertIn("if(started&&!fromVideo)seekChapter(active);", self.page)

    def test_suicide_chapter_carries_a_content_note(self):
        noted = [c["title"] for c in self.chapters if c.get("content_note") == "suicide"]
        self.assertEqual(noted, ["The terrible truth"])

    def test_has_its_own_palette(self):
        self.assertIn("--desk:#c8dbcd", self.page)
        self.assertNotIn("#f7f3eb", self.page)

class PublicationDates(unittest.TestCase):
    def test_index_and_sites_show_when_each_video_was_published(self):
        build(ROOT / "build.py")
        index = (ROOT / "index.html").read_text()
        self.assertIn("Published 20 September 2026", index)
        self.assertIn("Published 4 May 2026", index)
        self.assertIn("Published 10 August 2026", index)
        self.assertIn("Published 20 September 2026", (ROOT / "rick-rubin" / "index.html").read_text())
        self.assertIn("Published 4 May 2026", (ROOT / "jefferson-fisher" / "index.html").read_text())

if __name__ == "__main__":
    unittest.main()
