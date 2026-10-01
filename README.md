# Field notes

Close readings of long YouTube conversations, published on GitHub Pages. Each video gets its own static reading site in a subdirectory, and the root `index.html` lists them all. The shared behaviour lives in `field_notes/`; each site keeps its own form, look and data.

## Commands

The build needs PyYAML (`python3 -m pip install -r requirements.txt`); the browser tests also use Playwright when it is installed.

- `python3 -m field_notes build [<slug>]` renders a site from its `template.html` or `build.py`, and the root index from `videos.yaml`.
- `python3 -m field_notes breaks <slug>` writes `breaks.yaml` from SponsorBlock. Fill in the labels by hand; `--overwrite` replaces an existing file.
- `python3 -m field_notes index <slug> --transcript <path>` writes `transcript-index.json`, the word index search uses. The transcript itself stays outside this repository.
- `python3 -m field_notes check <slug> --transcript <path>` checks quotes, timestamps, breaks, typography and the design notes against the transcript.
- `python3 -m field_notes new <slug>` starts a site folder for an entry in `videos.yaml`.

## A site

A site folder holds its data (`chapters.yaml`, `wisdom.csv` or something new), `breaks.yaml`, `transcript-index.json`, a `README.md` with a `## Design` section, and a `build.py` with `build()`, `items()` and `prose()`. Its template carries three markers that the library fills: `<!-- field-notes:head -->`, `<!-- field-notes:published -->` and `<!-- field-notes:runtime -->`. The site script after the runtime marker renders its items and calls `FieldNotes.mount`.

## Checks

`python3 -m unittest discover -s tests` rebuilds every site and tests the library and each site, in Chromium where Playwright is available. `node --test 'tests/runtime/*.test.mjs'` tests the runtime on its own.
