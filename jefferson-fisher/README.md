# Jefferson Fisher: The quiet art of leading any conversation

A poster wall for the Modern Wisdom conversation between Jefferson Fisher and Chris Williamson. `wisdom.csv` holds 125 quotes with a score, situation, context and timestamp; `contexts.py` holds the longer context paragraphs that appear on the posters.

Run `python3 build.py` to render every quote as an SVG poster in `posters/` and rebuild `index.html`. Line breaks are fitted automatically; `HAND_SET_POSTERS` in `build.py` overrides the breaks and accent words for individual posters. `python3 poster.py <timestamp_s>` renders a single poster.
