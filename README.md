# Field notes

Close readings of long YouTube conversations, published on GitHub Pages. Each video gets its own standalone reading site in a subdirectory, and the root `index.html` lists them all.

## Adding a video

1. Create a subdirectory named after the speaker (for example `rick-rubin/`) with its own `index.html`.
2. Add an entry to `videos.yaml`.
3. Run `python3 build.py` to regenerate the root `index.html`.

The build scripts need PyYAML: `python3 -m pip install -r requirements.txt`. The pages themselves have no build step at runtime and open directly from disk.

Run `python3 -m unittest discover -s tests` to rebuild the pages and check their links.
