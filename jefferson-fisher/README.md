# Jefferson Fisher: The quiet art of leading any conversation

A poster wall for the Modern Wisdom conversation between Jefferson Fisher and Chris Williamson. `wisdom.csv` holds 125 quotes with a score, situation, context and timestamp; `contexts.py` holds the longer context paragraphs that appear on the posters.

Run `python3 build.py` to render every quote as an SVG poster in `posters/` and rebuild `index.html`. Line breaks are fitted automatically; `HAND_SET_POSTERS` in `build.py` overrides the breaks and accent words for individual posters. `python3 poster.py <timestamp_s>` renders a single poster.

## Design: the legal pad

Jefferson Fisher is a trial lawyer in Beaumont, Texas, and the conversation is about arguing well. The page takes its colours from the yellow legal pad lawyers write their arguments on: canary paper, blue legal rules, a double red margin and blue-black ballpoint. The only shape borrowed from the pad is the double red margin line on the title card; the posters stay white so the lines read as print, not as notes.

| Role | Colour | Reason |
|---|---|---|
| Page | `#ede3b0` | canary legal pad paper, a shade duller under office light |
| Title card | `#fbf5d4` | a fresh top sheet of the same pad |
| Text | `#1f2b3d` | blue-black ballpoint ink |
| Secondary text | `#5e6b7d` | the same ink pressed lightly |
| Rules and borders | `#a9c0d8` | the blue horizontal legal rule |
| Accent and margin | `#c33a2e` | the double red margin line, also the italic accent words on the posters |

The type is unchanged: a book serif for the title card and a grotesque for the small labels, with the posters set in Garamond. What read as generic in October 2026 is still the gradient, Inter and three-card look described in [Northeast Times](https://northeasttimes.com/2026/07/31/ai-design-tools-are-making-every-website-look-the-same/) and [925 Studios](https://www.925studios.co/blog/ai-slop-design-tells); the warm cream page with a terracotta accent that this site first shared with the Rick Rubin reading is gone.

Research: [Jefferson Fisher on Wikipedia](https://en.wikipedia.org/wiki/Joseph_Jefferson_Fisher), [canary legal pads with blue rules and a red margin](https://www.bluedogink.com/universal-perforated-ruled-writing-pads-wide-legal-rule-red-headband-50-canary-yellow-85-x-1175-sheets-dozen-10630.html), [the Mizzou store canary law pad](https://www.themizzoustore.com/Canary-Law-Legal-Pad).
