# Listening round 1, 2026-11-21

One listener (Ethan), laptop speakers, had never heard of the rule against parallel fifths.
Twelve blind pairs on the listening bench: nine chorales as written against arm A's repair,
two repeats with the sides swapped, one identical pair. `answers/` holds the answers as saved,
`key.json` the key, `trials.json` the order shown.

## Result

| Chorale | Pairs | Repair | Preferred | Sure |
|---|---|---|---|---|
| c09 | 1, 11 | alto G4 to Bb4, completing a chord | repair, then no difference on the repeat | fairly, faint |
| c01 | 2 | tenor C4 to G3 | original | fairly |
| c04 | 3 | alto passing note deleted | original | certain |
| c03 | 4 | bass E3 to G3; alto E4 to C5 | original | certain |
| c05 | 5, 12 | tenor B3 to D4 | original; identical pair heard as identical | fairly |
| c07 | 6 | alto G4 to Bb4; tenor passing note deleted | repair | certain |
| a2 | 7, 10 | four notes | original, both times | certain, then faint |
| c10 | 8 | tenor passing note deleted | original | certain |
| c06 | 9 | alto E4 to C#4 | no difference | fairly |

Original preferred in 6 of 9, repair in 2, no difference in 1. The identical pair was heard as
identical; one of the two repeats reproduced, the faint one did not. X was chosen 3 times and Y 5.

## What it means, and how sure

- The repairs satisfied the check and usually sounded worse. The agents were told to change as
  few notes as possible; nothing asked them to keep the music good.
- The listener never heard a parallel fifth as wrong.
- **Hypothesis H1, not established:** preference follows inner-voice motion, the same quantity the
  corpus comparison had flagged before anyone listened (attacks off the beat: model 3%, Bach 20%;
  entry N_ON_THE_BEAT). Checked against the notes (`analysis/motion.txt`): the repair changed
  motion in three chorales. Two went the predicted way (c04, c10, both certain). One went the
  other way (c07, certain: the original, which had one more passing note, was "too simplistic").
  The listener's own words fit H1 ("more notes in the counterpoint", "stomp stomp stomp",
  "boring"), but 2 of 3 is not evidence.
- An earlier reading sorted the repairs into three kinds and said the kind explained the
  preference. That put c07 in "completed a chord"; by measurement it did not complete one. The
  only repair that did (c09) won faintly and not on the repeat.
- Changing the chord or its bass note went with preferring the original in both cases where it
  happened (c03, a2). Two cases.

## How to test H1 properly

Hold melody and harmony fixed and change only motion, by rule, not by an agent's judgment:
"minus" deletes every off-beat note in the lower three voices; "plus" inserts stepwise passing
notes between chord notes a third apart until the off-beat rate is near Bach's. Check every
version with the lint so no version adds parallels. Write the prediction (preference rises with
motion) into this repo before the listener hears anything. Blind pairs, repeats and an identical
pair as in this round.

## Pinned, not resolved

1. **Phrases don't breathe** (flagged in pairs 1, 4, 6, 9; "phrases and endings" chosen as the
   first thing to change). All nine chorales are two-bar phrases ending on a two-beat note with
   no rest, in strict time. Bach marks a fermata about every 2.5 bars (20 chorales), usually over
   a one-beat note: the breath is the performer's. MIDI has no fermata and the renderer adds no
   time. Unexplained: why four of nine were flagged and not the rest. Test: strict against a
   one-beat hold at each phrase end, on the bench.
2. **Pair 9's chorale (c06) "skips to the extrapolation without establishing its thesis".** Not
   separated by chords per beat, time on the home chord, off-key notes or density. Lead: its
   first phrase ends on the dominant; the two chorales praised by name (c04, c10) are the only
   two whose first phrase ends on the home chord. Three others also end phrase one on the
   dominant and drew no complaint. In none of the nine does the opening bar ever return.
3. **A "signal screech"** at c03-repaired bar 6, a2-repaired bar 7, c06 bar 3 (both versions).
   The listener says it depends on the high note, the counterpoint and the surrounding notes
   together. Ruled out: beating between the synth's partials (predicted from the notes and
   measured in the audio; no correlation, flagged bars not peaks: `analysis/screech.py`) and
   clipping (files peak at 0.37 of full scale). Test: a probe page that loops the bar with each
   voice switchable, the tone switchable, and the echo off.
4. **Too short and undeveloped for use in a game.** No measure yet.
5. **The explainer** of every flagged parallel, as written beside its repair, is in `casebook/`.
