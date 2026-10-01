import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const FieldNotes = createRequire(import.meta.url)('../../field_notes/runtime/field-notes.js');

test('timecodes are padded hours, minutes and seconds', () => {
  assert.equal(FieldNotes.timecode(0), '00:00:00');
  assert.equal(FieldNotes.timecode(9971.6), '02:46:11');
});

test('the item playing is the last one that started, counting the lead', () => {
  const starts = [0, 100, 200];
  assert.equal(FieldNotes.itemPlayingAt(starts, 99, 2), 1);
  assert.equal(FieldNotes.itemPlayingAt(starts, 97, 2), 0);
  assert.equal(FieldNotes.itemPlayingAt([500, 100, 300], 350, 2), 2);
  assert.equal(FieldNotes.itemPlayingAt([100], 50, 2), -1);
});

test('breaks are found by time and placed before the first item after them', () => {
  const breaks = [{ start: 0, end: 150 }, { start: 3465, end: 3581 }, { start: 9972, end: 9990 }];
  assert.equal(FieldNotes.breakPlayingAt(breaks, 3500).start, 3465);
  assert.equal(FieldNotes.breakPlayingAt(breaks, 3581), null);
  assert.deepEqual(FieldNotes.itemAfterEachBreak([0, 64, 3619], breaks), [0, 2, 3]);
});

test('readings right after our own seek are ignored until the player reaches the target', () => {
  const filter = FieldNotes.createReadingFilter();
  assert.equal(filter.trust(500, 0), true);
  filter.seeked(1000, 1000);
  assert.equal(filter.trust(501, 2000), false);
  assert.equal(filter.trust(1001, 3000), true);
});

test('a seek that never arrives turns into a hold, as when an ad plays', () => {
  const filter = FieldNotes.createReadingFilter();
  filter.seeked(1000, 0);
  assert.equal(filter.trust(3, 9000), false);
  assert.equal(filter.trust(20, 20000), false);
  assert.equal(filter.trust(1002, 30000), true);
});

test('an ad that restarts the clock near zero holds the page until the video returns', () => {
  const filter = FieldNotes.createReadingFilter();
  assert.equal(filter.trust(1200, 0), true);
  assert.equal(filter.trust(2, 1000), false);
  assert.equal(filter.trust(15, 16000), false);
  assert.equal(filter.trust(1203, 31000), true);
});

test('a hold gives up after a few minutes', () => {
  const filter = FieldNotes.createReadingFilter();
  filter.trust(1200, 0);
  filter.trust(2, 1000);
  assert.equal(filter.trust(400, 200000), true);
});

test('content ranks by distinct words found, then hits, and marks the best sentence', () => {
  const docs = [{ text: 'Coding is fun. Vibes.' }, { text: 'Vibe coding and more vibe coding.' }, { text: 'Nothing here.' }];
  const found = FieldNotes.search('vibe coding', docs, [], [0, 10, 20], 2);
  assert.deepEqual(found.content.map(r => r.i), [1, 0]);
  assert.match(found.content[0].snippet, /<mark>Vibe<\/mark> <mark>coding<\/mark>/);
});

test('transcript hits need every word and are grouped per item in time order', () => {
  const windows = [[0, 'beat jay keep'], [30, 'beat coding vibe'], [60, 'coding vibe'], [300, 'coding vibe']];
  const found = FieldNotes.search('vibe coding', [], windows, [0, 200], 2);
  assert.deepEqual(found.transcript.map(h => [h.item, h.start, h.moments]), [[0, 30, 2], [1, 300, 1]]);
});

test('an empty query is not a search', () => {
  assert.equal(FieldNotes.search('  ', [], [], [], 2), null);
});

test('video links start the lead before the moment', () => {
  assert.equal(FieldNotes.videoLink('abc', 100, 2), 'https://youtu.be/abc?t=98');
  assert.equal(FieldNotes.videoLink('abc', 1, 2), 'https://youtu.be/abc?t=0');
});
