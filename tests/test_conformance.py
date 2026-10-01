"""Each site in a real browser, with a stand-in for the YouTube player.

The stand-in replaces https://www.youtube.com/iframe_api, so the tests run offline
and can move the video clock. Ads only appear on the live site; replay the player
there after a change to the sync.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parent.parent
FAKE_YOUTUBE = """
window.YT = {PlayerState: {PLAYING: 1, PAUSED: 2}, Player: class {
  constructor(id, options) { this.options = options; this.t = 0; this.seeks = []; window.fakePlayer = this;
    setTimeout(() => options.events.onReady({}), 0); }
  getCurrentTime() { return this.t; }
  seekTo(t) { this.t = t; this.seeks.push(t); }
  cueVideoById(o) { this.cued = o.startSeconds; }
  playVideo() {}
  play(at) { this.t = at; this.options.events.onStateChange({data: 1}); }
}};
window.onYouTubeIframeAPIReady();
"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(sync_playwright, "playwright is not installed")
class InTheBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "-m", "field_notes", "build"], cwd=ROOT, check=True, capture_output=True)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()

    def open(self, path):
        page = self.browser.new_page(viewport={"width": 1280, "height": 900})
        self.errors = []
        page.on("pageerror", lambda error: self.errors.append(str(error)))
        page.route("https://www.youtube.com/iframe_api", lambda route: route.fulfill(body=FAKE_YOUTUBE, content_type="text/javascript"))
        page.goto(self.base + path)
        page.wait_for_function("window.fakePlayer && window.fakePlayer.cued !== undefined")
        self.addCleanup(page.close)
        return page

    def hash(self, page):
        return page.evaluate("location.hash")

    def follow(self, page, seconds):
        page.evaluate(f"fakePlayer.t = {seconds}")
        page.wait_for_timeout(1100)

    def test_chapter_sites_link_navigate_and_go_back(self):
        for slug in ["rick-rubin", "jimmy-carr"]:
            with self.subTest(slug):
                page = self.open(f"/{slug}/index.html#page-3")
                self.assertTrue(page.is_visible("#page-3"))
                self.assertEqual(page.get_attribute("#toc li:not(.break) >> nth=2 >> a", "aria-current"), "true")
                page.click("#next")
                self.assertEqual(self.hash(page), "#page-4")
                page.keyboard.press("ArrowRight")
                self.assertEqual(self.hash(page), "#page-5")
                page.go_back()
                page.wait_for_function("location.hash === '#page-4'")
                self.assertTrue(page.is_visible("#page-4"))
                page.go_back()
                page.wait_for_function("location.hash === '#page-3'")
                self.assertEqual(self.errors, [])

    def test_the_title_page_has_no_address_and_cues_the_start(self):
        page = self.open("/rick-rubin/index.html")
        self.assertTrue(page.is_visible("#cover"))
        self.assertEqual(self.hash(page), "")
        self.assertEqual(page.evaluate("fakePlayer.cued"), 0)
        page.click("#begin")
        self.assertEqual(self.hash(page), "#page-1")
        page.go_back()
        page.wait_for_function("location.hash === ''")
        self.assertTrue(page.is_visible("#cover"))

    def test_the_page_follows_the_video_without_filling_the_history(self):
        page = self.open("/rick-rubin/index.html#page-1")
        length = page.evaluate("history.length")
        page.evaluate("fakePlayer.play(0)")
        self.follow(page, 3740)
        self.assertEqual(self.hash(page), "#page-32")
        self.assertTrue(page.is_visible("#page-32"))
        self.assertEqual(page.evaluate("history.length"), length)

    def test_an_ad_does_not_move_the_page(self):
        page = self.open("/rick-rubin/index.html#page-1")
        page.evaluate("fakePlayer.play(0)")
        self.follow(page, 3740)
        self.follow(page, 3)
        self.assertEqual(self.hash(page), "#page-32")

    def test_picking_a_chapter_after_playing_seeks_the_video(self):
        page = self.open("/jimmy-carr/index.html#page-1")
        page.evaluate("fakePlayer.play(0)")
        page.click("#toc li:not(.break) >> nth=9 >> a")
        start = page.evaluate("FIELD_NOTES.chapters[9].start - FIELD_NOTES.lead")
        self.assertEqual(page.evaluate("fakePlayer.seeks.at(-1)"), start)

    def test_break_markers_sit_between_the_chapters_around_them(self):
        page = self.open("/rick-rubin/index.html")
        labels = page.eval_on_selector_all("#toc > li", "items => items.map(li => li.className === 'break' ? 'break' : li.textContent.slice(0, 2))")
        self.assertEqual(labels[0], "break")
        sponsors = labels.index("break", 1)
        self.assertEqual(labels[sponsors - 1:sponsors + 2], ["30", "break", "31"])
        page.click("#begin")
        page.evaluate("fakePlayer.play(0)")
        self.follow(page, 3500)
        self.assertEqual(page.eval_on_selector_all("#toc .break.playing", "m => m.map(x => x.textContent)"), ["SponsorsKetone IQ and Fiverr"])

    def test_search_finds_the_site_and_the_spoken_transcript(self):
        page = self.open("/rick-rubin/index.html")
        page.fill("#q", "vibe coding")
        groups = page.eval_on_selector_all("#results .group", "g => g.map(x => x.textContent)")
        self.assertEqual(groups, ["In the chapters", "Spoken in the video"])
        page.fill("#q", "you just hit the reset button")
        self.assertIn("32 · The reset", page.inner_text("#results"))
        page.fill("#q", "fiverr")
        self.assertNotIn("Spoken in the video", page.inner_text("#results"))
        page.fill("#q", "catatonic")
        self.assertEqual(page.eval_on_selector_all("#results .group", "g => g.map(x => x.textContent)"), ["Spoken in the video"])
        page.click("#results a")
        self.assertEqual(self.hash(page), "#page-31")

    def test_the_poster_wall_follows_the_video_and_searches(self):
        page = self.open("/jefferson-fisher/index.html#p3721")
        self.assertEqual(page.eval_on_selector_all("li.current", "l => l.map(x => x.id)"), ["p3721"])
        page.evaluate("fakePlayer.play(0)")
        self.assertEqual(page.eval_on_selector_all("ol.wall li.break", "l => l.length"), 4)
        self.follow(page, 5552)
        self.assertEqual(self.hash(page), "#p5552")
        page.click("#p171 .poster")
        self.assertEqual(self.hash(page), "#p171")
        page.go_back()
        page.wait_for_function("location.hash === '#p5552'")
        page.fill("#q", "tennis")
        visible = page.eval_on_selector_all("ol.wall li:not(.break)", "l => l.filter(x => !x.hidden).length")
        self.assertEqual(visible, 1)
        self.assertIn("SPOKEN IN THE VIDEO", page.inner_text("#spoken").upper())
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
