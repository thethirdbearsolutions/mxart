# What was measured, 2026-11-21

One day, one model (the composing and repairing agents were all fresh sessions of the same
model). The raw tables are in `results/`; the prompts are in `PROMPTS.md`; `python3 mxart.py
explain` has the same findings attached to the codes they belong to.

## Reference music

| Set | Pieces | Notes | Source |
|---|---|---|---|
| Bach chorales | 36 | 8,739 | music21's bundled corpus |
| Corelli trio sonatas | 146 movements | 52,880 | DCMLab/corelli note tables (organ staff left out) |
| Haydn quartets | 37, cut into 152 single-metre stretches | 245,087 | OpenScore/StringQuartets |
| Saint-Georges quartets | 6, 11 stretches | 14,901 | OpenScore/StringQuartets |
| Haydn, mixed | 12 | 10,708 | Mutopia |
| Buxtehude | 4, 6 stretches | 3,643 | Mutopia |
| Hummel, preludes op. 67 | 22 | 3,039 | craigsapp/hummel-preludes |
| Essen folk songs | 34 | 1,759 | music21's bundled corpus |

The converted files are not in this repo; `bench/human.py` and `bench/extra.py` rebuild them.
Geminiani was looked for and not found.

## 1. Warnings written from intuition ran backwards

Per 100 notes (crossings per 100 bars):

| | Clash | Off-key | Crossing |
|---|---|---|---|
| Model chorales (all 26) | 0.86 | 2.19 | 0 |
| Corelli | 2.92 | 5.00 | 36 |
| Bach | 3.16 | 4.86 | 10 |
| Saint-Georges | 4.50 | 11.19 | |
| Haydn quartets | 4.88 | 12.77 | |
| Buxtehude | 5.16 | 6.37 | |
| Hummel | 8.09 | 10.46 | |

All three are now listed only by `lint --harmony`.

## 2. Parallel fifths: a fault the model makes and the composers don't

Mid-phrase (not following a note held two beats or more), per 1,000 paired voice moves:

| | Fifths | Octaves | Pieces with a mid-phrase fifth |
|---|---|---|---|
| Bach chorales | 0.7 | 0.1 | 5 of 36 |
| Corelli | 1.4 | 0.5 | 12 of 146 |
| Model chorales, first 10 (two agents, five each) | 7.4 | 6.5 | |
| Model chorales, next 16 (one agent each) | 7.2 | 0.0 | |
| Model chorales, all 26 | 7.3 | 2.4 | 14 of 26 |

- Hand check: every flagged case in the Bach and first model batch is a true perfect fifth in
  similar motion. Half of that batch's raw hits followed a held note; they are counted apart.
- music21's `VoiceLeadingQuartet` agrees on the model chorales (14 against 13 in the batch of 16).
- The octaves figure did not replicate: it was a habit of the two agents that wrote five each.
- Outside strict part-writing the octave count is meaningless (Haydn 204, Saint-Georges 142,
  Hummel 117 per 1,000: instruments double on purpose).

## 3. Fault injection into Bach (36 chorales, 5 trials each)

Caught = the lint prints a warning it did not print for the clean chorale.

| Injected | With clash/off-key/crossing on | Default lint now |
|---|---|---|
| One voice shadows another a fifth away | | 87% |
| A bar silent in every voice | 100% | 100% |
| One note an octave off | 64% | 63% |
| One voice a semitone sharp for a bar | 99% | 9% |
| One note a semitone off | 71% | 8% |
| Two bars stuck on one pitch | 71% | 7% |
| One voice a sixteenth late for a bar | 32% | 1% |

Demoting the three warnings cost nearly all ability to see a single wrong note.

## 4. Repair: ten faulty chorales, three arms, one fresh agent per chorale per arm

17 mid-phrase parallels going in.

| | A: mxart with lint | B: same text, no lint | C: plain Python |
|---|---|---|---|
| Parallels left | 0 | 2 | 0 |
| New contrary-motion fifths or octaves (music21) | 0 | 0 | 2 |
| Note events changed per chorale | 3.5 | 3.3 | 3.4 |
| Soprano notes changed | 0 | 0 | 0 |
| Median wall time | 18 s | 54 s | 41 s |
| Tokens per run | about 79k | about 82k | about 85k |

- B named all 17 parallels correctly. Its two leftovers are one chorale (c06) where the agent
  reported an edit that is not in the file.
- C's agents each wrote a checker. Two fixes moved a note an octave, turning parallel fifths
  into fifths by contrary motion; their checkers and mxart's pass that, music21 does not.
- One contrary-motion fifth in a2 was in the original and is in all three arms.
- B's agents were asked not to write checking code; this could not be enforced.

## 5. One sentence in the brief

Same sixteen keys and briefs, plus "Avoid parallel fifths and parallel octaves between voices."

| | Mid-phrase fifths | Per 1,000 moves | Pieces with a mid-phrase parallel | music21 |
|---|---|---|---|---|
| Without (c01-c16) | 13 | 7.2 | 9 of 16 | 14 |
| With (d01-d16) | 1 | 0.6 | 2 of 16 | 2 |

Median time to compose was about 4 minutes without and about 3 with; tokens were about the same.

## 6. What the sentence did not touch

Median per voice:

| | Attacks off the beat | Bars with a new rhythm |
|---|---|---|
| Model chorales, without the sentence | 3.4% | 38% |
| Model chorales, with it | 3.4% | 38% |
| Bach | 20.4% | 69% |
| Corelli | 32.5% | 50% |
| Haydn quartets | 42.4% | 23% |
| Buxtehude | 51.6% | 76% |

(The rhythm figure falls with length, so compare it only between sets of similar length.)

Also: the "half a track on one pitch" warning fires on no voice of 36 Bach chorales, on 8
voices of the 26 chorales without the sentence (5 altos, 3 tenors), and on 3 of the 16 with it.

## 7. Found by accident

- c13's soprano enters nine bars late (a tempo event with a delay before its first note). The
  lint says nothing. Of the 30 repair agents shown the piece, one noticed. The corpus figures
  above include c13 as written.
- `grid` counts cells per bar, so a 3/4 piece needs grid 12 where a 4/4 piece needs 16.
- At a sixteenth-note grid, notes that don't fit: Bach 0%, Corelli 0.3%, Saint-Georges 5.1%,
  Buxtehude 6.1%, Haydn mixed 7.9%, Haydn quartets 11.5%, Hummel 23.8%.

## Limits

- One model, one day, one class of fault tested end to end. Ten to sixteen pieces per arm.
- No person had listened when this was written. `listen/` holds nine blind pairs (original
  against arm A's repair) for that.
- Keys for the reference music are one estimate per stretch, so off-key counts in long
  movements mostly count modulation.
- The lint's thresholds for "monotone" and "leap" are guesses.
- The scripts under `bench/` and `repair/` are as they were run, with absolute paths under
  `/home/user`. They need those edited to run elsewhere.

## 8. A person listened (added later the same day)

One listener, blind, preferred the chorale as written over its repair in 6 of 9 pairs, and
never heard a parallel fifth as wrong. The full record, the corrected reading of it, and the
questions it opened are in `listening/round1/README.md`.
