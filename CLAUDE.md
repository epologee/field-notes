<!-- SYNCED with CIRCUS.md through 'circus sync'. Edit CIRCUS.md or this file; run 'circus sync' to align CLAUDE.md and AGENTS.md. -->

# Field notes

Field notes publishes one-off reading sites for long YouTube conversations, each in its own subdirectory, with a shared index at the root.

## One-offs, not a framework

Every conversation gets the form that suits it: thematic chapters for a single guest who develops arguments at length, a poster wall for a conversation full of standalone lines, or something new. Techniques that proved themselves on an earlier site are copied into the new site and adapted there. Do not extract a shared library or template that forces the sites into one shape.

Techniques worth copying from existing sites:

- source data in YAML or CSV, with a `build.py` that renders a standalone `index.html`
- video links that start `LEAD_S` seconds before the timestamp
- an embedded YouTube player that docks in a corner and keeps the page and the video in step in both directions, cues the chosen moment before the first play, and holds still while an ad reports its own time
- deep links to a single chapter or poster, full-text search, share preview metadata, and a print stylesheet without the video
- the publication date from YouTube in the header and on the index card

## Every site has its own look

Each site gets its own colour scheme and typography, derived from the subject of the conversation rather than from a house style. Do fresh design research for every new site; an earlier site's research does not carry over:

1. Search what currently reads as generic or machine-made in web design. The defaults drift over time, so look them up again instead of relying on the list below.
2. Search the subject itself for visual material: the guest's world, the objects and printed matter around their work, the era or place the conversation is about.
3. Name the theme, pick every colour as a hex value with a reason tied to the subject, and choose the type and the shapes.
4. Record the research sources and these decisions in the site's README.

As of September 2026 the recognisable defaults were purple-to-blue gradients with Inter, warm cream paper with a high-contrast serif and a terracotta accent, near-black with a single neon accent, and broadsheet layouts built from hairline rules. Treat that as an example of what to check for, not as the list to check against. Two sites next to each other on the index should not look like the same template with different words.

## From transcript to site

Read the whole transcript before choosing the form. When it is unclear which episode is meant, ask before reading, because the choice of episode decides everything after it. Take timestamps from phrases located in the transcript, never from estimates, and check that every quote falls inside its own chapter or poster. Quotes stay verbatim, sponsor reads are left out, and a chapter on a sensitive subject carries a content note.

## Checks

Run `python3 -m unittest discover -s tests` before committing. It rebuilds every page and checks their links, players and metadata. Test the player through a local HTTP server, because YouTube refuses to embed into a page opened from disk. After every push that touches a player, replay it on the live site: ads only appear there, and they are what breaks seeking.
