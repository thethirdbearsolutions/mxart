# Notebook: one day, 2026-11-21

A record of what was asked, what was tried, what turned out wrong, and where each thing lives.
Written so the day can be reconstructed without the conversation it happened in. "Ethan" is the
person; "the model" is the Claude session that did the work. Quotes are Ethan's own words.

## How it started

Ethan asked: what's the "midi equivalent of pxart", and does it exist yet? pxart is his tool for
pixel art as plain text with located checks. The model's first answer: the text formats exist
many times over (ABC, LilyPond, MML, Alda, tracker text); the loop for writing music you can't
hear mostly doesn't.

Asked whether pxart itself justifies its existence, the model first said yes for the tooling,
then read pxart's draft blog (31 posts) and found the blog's own tests show pxart does not make a
model draw better. Where it does help: checkable faults, small edits, palettes across a game,
payload on slow links. The model filed fourteen tickets (PX-1 to PX-14 in the Chaotic tracker)
proposing pxart be treated as a linter and build pipeline.

## The prototype

Ethan: "do you want to prototype the midi equivalent?" The model built `mxart.py` in one sitting:
a grid text format, `check`, `lint`, `roll`, `render`, `import`, `cmp`. Its own example tune
tripped its own clash warning on a major seventh, the first sign the guessed warnings were off.

## The loop, and its order

Ethan: "What kind of loop would tell you how to iterate on it and whether?" The model proposed
five steps with a stop condition each, base rate first. Ethan: "How can you do one without first
doing two?" He was right: counting faults with an uncalibrated lint is circular. The order became
corpora first, injection second, comparison third.

## What the corpora said

- Reference music: Bach chorales and Essen folk songs, then at Ethan's request Haydn,
  Saint-Georges, Buxtehude, Hummel and Corelli. Geminiani could not be found.
- The guessed warnings (clash, off-key, later crossing) fired more on every composer than on the
  model. They were demoted.
- A check nobody had guessed, parallel fifths, separated the model from everyone: about 7 per
  1,000 paired moves against Bach's 0.7 and Corelli's 1.4. A hand check halved the first figure
  (phrase breaks). A second batch of 16 chorales, one fresh agent each, replicated it; the
  parallel-octaves figure did not replicate.
- Plain description found a gap no rule named: the model's voices attack off the beat 3% of the
  time, Bach's 20%.

## Two attempts to kill it

1. **Repair test.** Ten faulty chorales, three arms: with the lint, the same text without it, and
   plain Python. All three fixed nearly everything. The lint was faster and confirmed its edits.
2. **One sentence.** Sixteen fresh chorales with "Avoid parallel fifths and parallel octaves
   between voices" in the brief: 0.6 per 1,000, Bach's rate, at no cost.

The model concluded: stop building mxart as a linter.

## The turn

Ethan: "I have a strong intuition there's value here you're not seeing by construction and can't
name it."

Naming the construction found it. Every test was one agent, one short piece, one sitting, a fault
already named, no person. The tests could not see: that the sentence was free only after an
instrument said which sentence to write; faults with no name yet; time and scale; a shared
language with a person; operations rather than checks.

Ethan: "Yes all of the above bingo and a home as code (and as error codes) for the knowledge
base. The old 'jQuery is an encyclopedia of browser compatibility quirks, not a library' line.
(Or did I write that line myself in 2007? Is it a known line?)" The model could not place the
line with anyone and did not search.

Out of that: `mxart explain` and `mxart brief`. Each code is an entry with what was measured, when
it is wrong, its status, and the sentence that prevents it. Demoted warnings and findings with no
check are entries too.

## A person listens

Ethan found the zip of pairs hard to use: "it's hard to know what to do with my listening ears
with this zip." The model built a listening bench (a page with a switching player, fixed
questions, notes, repeats and an identical pair, answers saved where the model can read them).

Result: he preferred the chorale as written over its repair in 6 of 9, never heard a parallel
fifth as wrong, passed the identical pair, and reproduced his clear preference on the repeat.
His notes named things no check had: phrases that don't breathe ("a stately tune of grandeur
played on a forced march with a bayonet pressed against the small of its back"), a piece that
"skips straight to the extrapolation without first establishing its thesis", a "signal screech".
Mid-test he wrote: "I think I understand what parallel fifths means now?"

The model first read the result as "the kind of fix mattered" and tied it to the motion gap the
corpus had already flagged. Ethan: "it's seriously crazy to me if it holds since it's both
predictive, measurable, and *flagged in advance as a lint gap*". Checking it against the notes,
the model found it had overstated: motion changed in three repairs, two went the predicted way
and one, certain, went the other. It is recorded as a hypothesis with a test designed for it
(`listening/round1/README.md`).

## Mistakes worth keeping

- Proposed measuring a base rate with an unvalidated instrument (caught by Ethan).
- Reported parallel fifths at 16 times Bach's rate before a hand check; it is 5 to 10 times.
- Reported parallel octaves as a model fault; it was two agents' habit.
- Concluded "stop" from tests that could only see one kind of value (caught by Ethan).
- Guessed the screech was beating between overtones, then clipping; both measured and ruled out.
- Sorted repairs into kinds and said the kind explained the preference; one chorale was in the
  wrong kind and the pattern is 2 of 3.
- The first format had `grid` as cells per bar, which silently mis-imports 3/4.

## Where things are

- This repo: the tool, `RESULTS.md` (tables), `PROMPTS.md` (briefs as sent), `bench/`, `repair/`,
  `listening/round1/` (answers, key, the exact audio heard, the bench page, analyses, casebook).
- Listening bench: https://claude.ai/artifact/HpFm2Ysvk3u4nsokXLxCd9 (private to Ethan)
- Parallel Fifths Casebook: https://claude.ai/artifact/WKqeXCZcyrKQF45C8nmC8U (private to Ethan)
- Chaotic tracker: PX-1 to PX-14 (pxart priorities; PX-1 carries the knowledge-base reframe),
  BLOG-78 (a blog pitch, "A linter is an encyclopedia, not a guard", awaiting Ethan).
- Not in the repo: the converted reference corpora (`bench/human.py` and `bench/extra.py` rebuild
  them), and the working conversation itself.

## Open threads

- Test H1 (preference follows motion) with rule-made versions and a prediction written first.
- Breath test: strict time against a held beat at phrase ends.
- A probe page to pin down the screech.
- The opening-phrase lead for "no thesis"; "too short and undeveloped for a game" has no measure.
- Other genres Ethan named: true chiptunes, Uematsu, sacred works, more folk tunes, shanties,
  pavanes and courtly dance.
- Fruitapella's music, which Ethan says is generally great but has some checkable bugs.
- Listening with chorales written with and without the one sentence.
- The repo has no licence file.
