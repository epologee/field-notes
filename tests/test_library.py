"""The shared field_notes library: data, breaks, transcript index, checks and rendering."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from field_notes import breaks, checks, render, transcript, typography  # noqa: E402
from field_notes.episode import Break, Item, Quote, check_label, timecode  # noqa: E402

TRANSCRIPT = """# A conversation

[00:00:00] **S0:** When I played him the beat he said keep playing it.
[00:00:20] And the label said it would never be a single.
[00:00:40] **S1:** That's the idea behind our sponsor, a drink.
[00:01:10] **S0:** You just hit the reset button and start again.
"""


def segments():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(TRANSCRIPT)
    return transcript.read(handle.name)


class Timecodes(unittest.TestCase):
    def test_labels_must_agree_with_their_seconds(self):
        self.assertEqual(timecode(3736), "01:02:16")
        self.assertEqual(check_label("01:02:16", 3736, "chapter"), 3736)
        with self.assertRaises(ValueError):
            check_label("01:02:15", 3736, "chapter")


class SponsorBlockBreaks(unittest.TestCase):
    def test_overlapping_segments_merge_under_the_category_covering_most(self):
        found = breaks.merge([
            {"category": "preview", "segment": [0, 122.5]},
            {"category": "interaction", "segment": [122.5, 149.2]},
            {"category": "selfpromo", "segment": [123, 152.5]},
            {"category": "sponsor", "segment": [3465.5, 3580.9]},
            {"category": "sponsor", "segment": [7253.5, 7323]},
            {"category": "selfpromo", "segment": [7254.3, 7340.2]},
        ])
        self.assertEqual([(b["kind"], b["start_s"], b["end_s"]) for b in found],
                         [("Cold open", 0, 152), ("Sponsors", 3465, 3581), ("Promotion", 7253, 7340)])

    def test_written_breaks_read_back_with_checked_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "breaks.yaml").write_text(breaks.to_yaml([{"kind": "Sponsors", "label": "A drink", "start_s": 40, "end_s": 70}]))
            from field_notes.episode import breaks as read_breaks
            self.assertEqual(read_breaks(folder), [Break("Sponsors", "A drink", 40, 70)])


class TranscriptIndex(unittest.TestCase):
    def test_reads_timecoded_lines_without_speaker_labels(self):
        found = segments()
        self.assertEqual([s.start for s in found], [0, 20, 40, 70])
        self.assertEqual(found[2].text, "That's the idea behind our sponsor, a drink.")

    def test_publishes_sorted_distinct_words_per_window_without_running_text(self):
        published = transcript.index(segments())
        windows = published["windows"]
        self.assertIn("the", published["stopwords"])
        self.assertEqual([start for start, _ in windows], [0, 30, 60])
        first = windows[0][1].split(" ")
        self.assertEqual(first, sorted(set(first)))
        self.assertIn("playing", first)
        self.assertNotIn("the", first)
        self.assertNotIn("keep playing", windows[0][1])

    def test_a_window_starts_again_where_an_item_starts(self):
        windows = transcript.index(segments(), item_starts=[0, 20])["windows"]
        self.assertEqual([start for start, _ in windows], [0, 20, 30, 60])
        self.assertIn("label", windows[1][1])

    def test_sponsor_reads_stay_out_of_the_index_but_the_cold_open_stays_in(self):
        windows = transcript.index(segments(), [Break("Cold open", "", 0, 10), Break("Sponsors", "A drink", 40, 60)])["windows"]
        self.assertIn("beat", windows[0][1])
        self.assertNotIn("sponsor", " ".join(w for _, w in windows))


class Checks(unittest.TestCase):
    def test_a_clean_item_list_passes(self):
        items = [Item("Keep playing", 0, [Quote("keep playing it", 0)]), Item("Reset", 60, [Quote("You just hit the reset button", 70)])]
        self.assertEqual(checks.problems(items, [], segments()), [])

    def test_paraphrased_misplaced_and_interrupted_items_fail(self):
        items = [
            Item("Keep playing", 0, [Quote("just keep it playing", 0)]),
            Item("Sponsored", 45, []),
            Item("Reset", 60, [Quote("You just hit the reset button", 30)]),
        ]
        found = checks.problems(items, [Break("Sponsors", "A drink", 40, 60)], segments())
        self.assertTrue(any("present it as a paraphrase" in p for p in found))
        self.assertTrue(any("inside the sponsors break" in p for p in found))
        self.assertTrue(any("falls outside its item" in p for p in found))

    def test_a_quote_may_differ_slightly_from_an_imperfect_transcript(self):
        items = [Item("Reset", 60, [Quote("You just hit the reset button and you start again", 70)])]
        self.assertEqual(checks.problems(items, [], segments()), [])

    def test_a_paraphrase_is_not_held_to_the_spoken_words(self):
        items = [Item("Reset", 60, [Quote("Starting over is always allowed", 70, verbatim=False)])]
        self.assertEqual(checks.problems(items, [], segments()), [])
        items = [Item("Reset", 60, [Quote("Starting over is always allowed", 70)])]
        self.assertTrue(any("present it as a paraphrase" in p for p in checks.problems(items, [], segments())))

    def test_items_may_start_in_the_cold_open(self):
        items = [Item("Keep playing", 0, [])]
        self.assertEqual(checks.problems(items, [Break("Cold open", "", 0, 30)], segments()), [])

    def test_items_must_follow_the_video_unless_the_site_orders_them_otherwise(self):
        items = [Item("Late", 60, []), Item("Early", 0, [])]
        self.assertTrue(checks.problems(items, [], segments()))
        self.assertEqual(checks.problems(items, [], segments(), ordered=False), [])


class Typography(unittest.TestCase):
    def test_flags_straight_quotes_hyphens_and_dots(self):
        self.assertEqual(typography.prose_problems("x", "It’s “fine” … really"), [])
        found = typography.prose_problems("x", "It's \"fine\" -- really ... ok - yes")
        self.assertEqual(len(found), 5)

    def test_the_readme_records_design_research(self):
        with tempfile.TemporaryDirectory() as folder:
            readme = Path(folder) / "README.md"
            readme.write_text("# Site\n")
            self.assertTrue(typography.design_problems(folder))
            readme.write_text("# Site\n\n## Design: tickets\n\nRed `#d1242f`, from [roll tickets](https://example.com).\n")
            self.assertEqual(typography.design_problems(folder), [])


class Rendering(unittest.TestCase):
    TEMPLATE = ("<head><!-- field-notes:head --><style>:root{--ink:#111;--paper:#fff;--accent:#c00}</style></head>"
                "<body><!-- field-notes:published --><!-- field-notes:runtime --></body>")

    def test_fills_head_date_runtime_and_data(self):
        page = render.page(self.TEMPLATE, "rick-rubin", "Title", "About", {"note": "</script>"})
        self.assertIn('<meta property="og:image" content="https://i.ytimg.com/vi/a_GiFiHXJ6g/maxresdefault.jpg">', page)
        self.assertIn("Published 20 September 2026", page)
        self.assertIn("function mount(site)", page)
        self.assertIn('const FIELD_NOTES={"video":"a_GiFiHXJ6g","note":"<\\/script>"}', page)
        self.assertLess(page.index("text-wrap:pretty"), page.index("--ink:#111"))

    def test_refuses_a_template_without_markers_or_colour_tokens(self):
        with self.assertRaises(ValueError):
            render.page("<body></body>", "rick-rubin", "Title", "About", {})
        with self.assertRaises(ValueError):
            render.page(self.TEMPLATE.replace("--accent:#c00", ""), "rick-rubin", "Title", "About", {})


if __name__ == "__main__":
    unittest.main()
