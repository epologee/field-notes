# Rick Rubin: The creative act

`chapters.yaml` is the editable source for all 71 thematic chapters. Each chapter has a `timestamp_s` value in seconds; these seconds generate YouTube `?t=` links in `index.html`. Optional `continue_timestamp_s` and `quote_timestamp_s` values deep-link to additional moments. Every link starts `LEAD_S` seconds (set in `build.py`) before its timestamp, so the first word is not clipped.

Edit titles or paragraphs in `chapters.yaml`, then rebuild with `python3 build.py`.
