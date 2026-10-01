# Field notes

Field notes publishes reading sites for long YouTube conversations, each in its own subdirectory, with a shared index at the root. Every site is a single static `index.html` on GitHub Pages: no server, no API, no database and no serverless function, now or later.

## Shared behaviour, free form

Every conversation gets the form that suits it: thematic chapters for a single guest who develops arguments at length, a poster wall for a conversation full of standalone lines, or something new. The form, the layout and the look belong to the site.

The behaviour every site needs lives once in `field_notes/` and is inlined into each page at build time:

- `field_notes/runtime/field-notes.js`: the embedded YouTube player that keeps page and video in step in both directions, deep links and browser history, keyboard navigation, search over the site content and over the transcript index, and the placement of break markers
- `field_notes/base.css`: typographic hygiene only, never colours or fonts
- `field_notes/*.py`: loading and validating site data, the transcript index, ad breaks from SponsorBlock, the checks, the typography lint and rendering

A site supplies its own template, styles and render hooks, and calls `FieldNotes.mount`. Change shared behaviour in `field_notes/`, never in a site; a fix there reaches every site on the next build. Do not move layout, colour or type into `field_notes/`. The library is written for this repository alone: no packaging, no versioned API, no documentation for outside users.

## A new site

The editorial work of a new site, from transcript to published page, ships as the `field-notes:new-site` skill in `packages/field-notes/`; this repository is its own single-plugin marketplace for Claude Code and Codex. Edit the skill there, then regenerate the Codex adapters under `.agents/plugins/`.

## Every site has its own look

Each site gets its own colour scheme and typography, derived from the subject of the conversation rather than from a house style. Do fresh design research for every new site; an earlier site's research does not carry over:

1. Search what currently reads as generic or machine-made in web design. The defaults drift over time, so look them up again instead of relying on the list below.
2. Search the subject itself for visual material: the guest's world, the objects and printed matter around their work, the era or place the conversation is about.
3. Name the theme, pick every colour as a hex value with a reason tied to the subject, and choose the type and the shapes.
4. Record the research sources and these decisions in the site's README under a `## Design` heading.

As of September 2026 the recognisable defaults were purple-to-blue gradients with Inter, warm cream paper with a high-contrast serif and a terracotta accent, near-black with a single neon accent, and broadsheet layouts built from hairline rules. Treat that as an example of what to check for, not as the list to check against. Two sites next to each other on the index should not look like the same template with different words.

## Content rules

Words shown as a quote, with quotation marks or as a line attributed to the speaker, are what the speaker said, apart from the small corrections a transcript needs; the check accepts them at 85% likeness to the transcript. Words that drift further are a paraphrase: the page then presents them without quotation marks and without suggesting they were said that way, or leaves them out. Whether a site is built on quotes or on paraphrase follows from what the site is for, decided per site and where needed per item. Every quote falls inside its own chapter or poster. Timestamps come from phrases located in the transcript, never from estimates. Sponsor reads are left out of the text and appear only as break markers. A chapter or poster may start in the cold open, which replays excerpts of the conversation, but never inside any other break. A chapter on a sensitive subject carries a content note. The transcript itself is never published: a page carries only the word index that search needs, without running text.

## Checks

Run `python3 -m unittest discover -s tests` and `node --test 'tests/runtime/*.test.mjs'` before committing. Together they rebuild every page and check the library, the data and the behaviour in a browser. `python3 -m field_notes check <slug> --transcript <path>` checks quotes, timestamps and breaks against the transcript, which stays outside this repository. Look at every visual change in the browser yourself before committing, and name what you expected to see in the commit's `Visual:` trailer. Test the player through a local HTTP server, because YouTube refuses to embed into a page opened from disk. After every push that touches a player, replay it on the live site: ads only appear there, and they are what breaks seeking.
