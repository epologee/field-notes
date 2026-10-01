---
name: new-site
description: Builds a field notes reading site for a long YouTube conversation, with chapters or posters, a synced player, search and break markers. Use when the operator asks for field notes, a reading site, chapters or posters for a YouTube episode or podcast.
user-invocable: true
---

# A new field notes site

A field notes site is one static page per conversation in the field-notes repository. The shared behaviour comes from its `field_notes/` library; the editorial work and the look are yours. The repository's `CIRCUS.md` (also `CLAUDE.md` and `AGENTS.md`) holds the rules that every site keeps. Read it first; this skill only adds the order of work.

Work in the field-notes checkout: the folder whose root holds `field_notes/` and `videos.yaml`. If the session started elsewhere, find it or ask for it.

## 1. Settle the episode

Name the episode back to the operator with its show, guest and YouTube id. When more than one episode fits the request, ask before reading anything: the choice of episode decides everything after it.

## 2. Get the transcript

The library needs a timecoded Markdown transcript with lines like `[00:12:30] text`, optionally with `**S1:**` speaker labels. The operator keeps transcripts outside this repository. Look the episode up before asking: search the local repositories and transcript collections on this machine for its YouTube id or title. When no transcript exists yet, make one with the transcription tooling this session has. Ask the operator only when both come up empty. The transcript is source material only: never copy it into the repository. Only the word index goes in.

## 3. Start the site

1. Add the episode to `videos.yaml`: slug, title, speaker, show, host, YouTube id, duration, publication date from YouTube, the date added, a contents line and a one-sentence summary.
2. `python3 -m field_notes new <slug>` creates the folder with a template and a README.
3. `python3 -m field_notes breaks <slug>` writes `breaks.yaml` from SponsorBlock. Read the transcript at each break, name the sponsor or promotion in its label, and add any break SponsorBlock missed, such as an outro.
4. `python3 -m field_notes index <slug> --transcript <path>` writes the word index.

## 4. Read, then choose the form

Read the whole transcript before choosing anything. Chapters suit one guest who builds arguments at length; a poster wall suits a conversation full of standalone lines; something else may suit this one better. Copy the closest existing site's `build.py`, template and site script as a starting point, then make them this site's own.

Write every item from the transcript: timestamps come from phrases you located, and a quote sits inside its own item. Decide per site, and where needed per item, whether the words are a quote or a paraphrase, from what the page is for. A page built on what someone said keeps their words: copy them as spoken, allowing only the small corrections a transcript needs, and mark them `verbatim`. A page about the ideas may paraphrase, but then it presents the words without quotation marks and without suggesting they were said that way. When a line drifts too far from the transcript to pass as a quote, drop the quotation and keep it as a paraphrase, or leave it out. Leave sponsor reads out of the text; they appear only as break markers. Give an item on a sensitive subject a content note.

## 5. Give it its own look

Do the design research described in `CIRCUS.md` fresh for this site and record it in the README under `## Design`, with every colour as a hex value, its reason and the sources as links. Set at least `--ink`, `--paper` and `--accent` in the template. Keep layout, colour and type in the site, never in `field_notes/`.

## 6. Check until clean

1. `python3 -m field_notes check <slug> --transcript <path>` must report 0 problems. It finds paraphrased quotes, quotes outside their item, items inside a break, straight quotes and a missing design section. Fix the data, not the check.
2. `python3 -m unittest discover -s tests` and `node --test 'tests/runtime/*.test.mjs'` must pass. Add the site to the site and browser tests.
3. Serve the repository over HTTP and look at the page yourself at desktop and phone width: the title page, a deep link to an item, search for a word that only appears in the transcript, the break markers. Show the operator the screenshots and iterate on what they say.

## 7. Deliver

Commit through the repository's usual flow. Pushing publishes the site; follow the repository's push rules. After the push, play the live page: open an item by deep link, play through an ad, move to another item and use the back button. Ads only appear on the live site.
