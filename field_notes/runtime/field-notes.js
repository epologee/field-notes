(function (root) {
  'use strict';

  const SEEK_TOLERANCE_S = 3;
  const SEEK_TIMEOUT_MS = 8000;
  const AD_RESTART_FROM_S = 30;
  const AD_RESTART_TO_S = 5;
  const HOLD_DISTANCE_S = 30;
  const HOLD_TIMEOUT_MS = 180000;
  const HUMAN_INPUT_MS = 3000;
  const SNIPPET_CHARS = 170;
  const TRANSCRIPT_RESULTS = 30;

  function timecode(seconds) {
    const n = Math.max(0, Math.floor(Number(seconds)));
    const pad = v => String(v).padStart(2, '0');
    return `${pad(Math.floor(n / 3600))}:${pad(Math.floor(n % 3600 / 60))}:${pad(n % 60)}`;
  }

  function words(text) {
    return String(text).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').match(/[\p{L}\p{N}]+/gu) || [];
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  }

  function itemPlayingAt(starts, t, lead) {
    let found = -1;
    starts.forEach((start, i) => {
      if (start <= t + lead && (found < 0 || start >= starts[found])) found = i;
    });
    return found;
  }

  function breakPlayingAt(breaks, t) {
    return breaks.find(b => b.start <= t && t < b.end) || null;
  }

  function itemAfterEachBreak(starts, breaks) {
    return breaks.map(b => {
      const i = starts.findIndex(start => start >= b.start);
      return i < 0 ? starts.length : i;
    });
  }

  function createReadingFilter() {
    let ownSeek = null, adHold = null, lastTrusted = 0;
    return {
      seeked(to, now) { ownSeek = { to, at: now }; },
      trust(t, now) {
        if (ownSeek) {
          const reachedTarget = Math.abs(t - ownSeek.to) <= SEEK_TOLERANCE_S;
          if (!reachedTarget) {
            if (now - ownSeek.at < SEEK_TIMEOUT_MS) return false;
            adHold = { t: ownSeek.to, at: now };
            ownSeek = null;
            return false;
          }
          ownSeek = null;
          adHold = null;
        } else if (adHold) {
          const stillAway = Math.abs(t - adHold.t) > HOLD_DISTANCE_S;
          if (stillAway && now - adHold.at < HOLD_TIMEOUT_MS) return false;
          adHold = null;
        } else if (lastTrusted > AD_RESTART_FROM_S && t < AD_RESTART_TO_S) {
          adHold = { t: lastTrusted, at: now };
          return false;
        }
        lastTrusted = t;
        return true;
      },
    };
  }

  const hitsIn = (list, terms) => terms.map(t => list.filter(w => w.startsWith(t)).length);
  const queryTerms = q => [...new Set(words(q))];

  function rankByHits(docs, terms) {
    return docs.map((d, i) => {
      const perTerm = hitsIn(d.words, terms);
      return { i, found: perTerm.filter(Boolean).length, hits: perTerm.reduce((a, b) => a + b, 0) };
    }).filter(r => r.hits).sort((a, b) => b.found - a.found || b.hits - a.hits || a.i - b.i);
  }

  function snippet(text, terms) {
    const sentences = String(text).match(/[^.!?]+[.!?]*[”"]?/g) || [String(text)];
    let best = sentences.map(s => [hitsIn(words(s), terms).reduce((a, b) => a + b, 0), s])
      .sort((a, b) => b[0] - a[0])[0][1].trim();
    if (best.length > SNIPPET_CHARS) best = best.slice(0, SNIPPET_CHARS - 3).replace(/\s+\S*$/, '') + '…';
    return escapeHtml(best).replace(/[\p{L}\p{N}’']+/gu, w => {
      const n = words(w)[0];
      return n && terms.some(t => n.startsWith(t)) ? `<mark>${w}</mark>` : w;
    });
  }

  function search(query, docs, transcriptWindows, starts, lead) {
    const terms = queryTerms(query);
    if (!terms.length) return null;
    const content = rankByHits(docs.map(d => ({ words: words(d.text) })), terms)
      .map(r => ({ ...r, terms, snippet: snippet(docs[r.i].text, terms) }));
    const byItem = new Map();
    rankByHits(transcriptWindows.map(([, w]) => ({ words: w.split(' ') })), terms)
      .filter(r => r.found === terms.length)
      .map(r => transcriptWindows[r.i][0])
      .sort((a, b) => a - b)
      .forEach(start => {
        const item = itemPlayingAt(starts, start, lead);
        const moment = byItem.get(item) || { item, start, moments: 0, terms };
        moment.moments += 1;
        byItem.set(item, moment);
      });
    const transcript = [...byItem.values()].slice(0, TRANSCRIPT_RESULTS);
    return { terms, content, transcript };
  }

  function contentNote(note, explanation) {
    return `<strong>Content note: ${escapeHtml(note)}.</strong> ${explanation} If you or someone else may be in immediate danger, contact local emergency services or crisis support.`;
  }

  function videoLink(video, seconds, lead) {
    return `https://youtu.be/${video}?t=${Math.max(0, Math.floor(seconds) - lead)}`;
  }

  function centreInList(container, el, horizontal) {
    if (!container || !el) return;
    const box = container.getBoundingClientRect(), child = el.getBoundingClientRect();
    container.scrollTo(horizontal
      ? { left: container.scrollLeft + child.left - box.left - (container.clientWidth - child.width) / 2, behavior: 'smooth' }
      : { top: container.scrollTop + child.top - box.top - (container.clientHeight - child.height) / 2, behavior: 'smooth' });
  }

  function mount(site) {
    const lead = site.lead;
    const items = site.items;
    const starts = items.map(item => item.start);
    const breaks = site.breaks || [];
    const readings = createReadingFilter();
    const indexOfHash = new Map(items.map((item, i) => ['#' + item.hash, i]));
    const TITLE_PAGE = -1;
    let player = null, ready = false, started = false, ticker = null;
    let active = TITLE_PAGE, playingBreak = null, humanUntil = 0;

    for (const ev of ['wheel', 'touchmove', 'keydown']) {
      addEventListener(ev, () => { humanUntil = Date.now() + HUMAN_INPUT_MS; }, { passive: true });
    }

    function cue(seconds) {
      if (ready && !started) player.cueVideoById({ videoId: site.video, startSeconds: Math.max(0, seconds) });
    }

    function seek(seconds) {
      const to = Math.max(0, seconds);
      readings.seeked(to, Date.now());
      player.seekTo(to, true);
      if (site.playOnSelect) player.playVideo();
    }

    function markCurrent(i) {
      if (!site.mark) return;
      items.forEach((_, n) => {
        const el = site.mark(n);
        if (!el) return;
        if (n === i) el.setAttribute('aria-current', 'true');
        else el.removeAttribute('aria-current');
      });
    }

    function remember(url, cause) {
      if (cause === 'reader') history.pushState(null, '', url);
      if (cause === 'video') history.replaceState(null, '', url);
    }

    function go(i, cause = 'reader', playFrom = null) {
      if (i < 0) return showTitlePage(cause);
      i = Math.max(0, Math.min(items.length - 1, i));
      if (i !== active) remember('#' + items[i].hash, cause);
      active = i;
      markCurrent(i);
      const from = (playFrom ?? items[i].start) - lead;
      const readerMoved = cause === 'reader' || cause === 'history';
      if (readerMoved && started) seek(from);
      else cue(from);
      site.activate(i, cause);
    }

    function showTitlePage(cause = 'reader') {
      if (!site.titlePage) return;
      if (active !== TITLE_PAGE) remember(location.pathname + location.search, cause);
      active = TITLE_PAGE;
      markCurrent(TITLE_PAGE);
      cue(0);
      site.activate(TITLE_PAGE, cause);
    }

    function readingOrder() { return site.readingOrder ? site.readingOrder() : items.map((_, i) => i); }

    function begin() {
      if (!started) return go(readingOrder()[0]);
      const now = player.getCurrentTime();
      const i = itemPlayingAt(starts, now, lead);
      go(i < 0 ? 0 : i, 'reader', now + lead);
    }

    function step(by) {
      if (active === TITLE_PAGE) return by > 0 ? begin() : undefined;
      const order = readingOrder();
      const next = order.indexOf(active) + by;
      if (next < 0) return showTitlePage();
      if (next < order.length) go(order[next]);
    }

    function followVideo() {
      if (site.titlePage && active === TITLE_PAGE) return;
      const t = player.getCurrentTime();
      if (!readings.trust(t, Date.now())) return;
      const b = breakPlayingAt(breaks, t);
      if (b !== playingBreak) {
        playingBreak = b;
        if (site.onBreak) site.onBreak(b);
      }
      const i = itemPlayingAt(starts, t, lead);
      if (i >= 0 && i !== active) go(i, 'video');
    }

    function showLocation(cause) {
      const i = indexOfHash.get(location.hash);
      if (i !== undefined) return go(i, cause);
      if (site.titlePage) return showTitlePage(cause);
      active = TITLE_PAGE;
      markCurrent(TITLE_PAGE);
      site.activate(TITLE_PAGE, cause);
    }

    addEventListener('popstate', () => showLocation('history'));
    addEventListener('keydown', e => {
      if (e.target.closest && e.target.closest('input,textarea,select,[contenteditable]')) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft') step(-1);
    });

    root.onYouTubeIframeAPIReady = () => {
      player = new YT.Player(site.playerId || 'player', {
        videoId: site.video,
        playerVars: { rel: 0, playsinline: 1 },
        events: {
          onReady: () => {
            ready = true;
            cue(active === TITLE_PAGE ? 0 : items[active].start - lead);
          },
          onStateChange: e => {
            clearInterval(ticker);
            if (e.data !== YT.PlayerState.PLAYING) return;
            if (!started) {
              started = true;
              if (site.onFirstPlay) site.onFirstPlay();
            }
            ticker = setInterval(followVideo, 1000);
            followVideo();
          },
        },
      });
    };
    const apiScript = document.createElement('script');
    apiScript.src = 'https://www.youtube.com/iframe_api';
    document.head.append(apiScript);

    showLocation('load');

    return {
      go,
      showTitlePage,
      begin,
      next: () => step(1),
      previous: () => step(-1),
      active: () => active,
      started: () => started,
      readerScrolledRecently: () => Date.now() < humanUntil,
      link: seconds => videoLink(site.video, seconds, lead),
      search: (query, docs) => search(query, docs, site.transcript || [], starts, lead),
      itemAfterEachBreak: () => itemAfterEachBreak(starts, breaks),
    };
  }

  const FieldNotes = {
    mount, timecode, words, escapeHtml, itemPlayingAt, breakPlayingAt, itemAfterEachBreak,
    createReadingFilter, rankByHits, snippet, search, contentNote, videoLink, centreInList,
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = FieldNotes;
  else root.FieldNotes = FieldNotes;
})(typeof window !== 'undefined' ? window : globalThis);
