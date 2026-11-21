# mxart (prototype)

Music as text, built as a linter from the start. A tune is a plain-text grid that renders to
MIDI; the tool's job is to say what is wrong with it, with a code, a place and a number.

It will not make a tune better. It catches the bar that's a cell short, the lead that clashes
with the pad on the beat, the melody that is 62% one note.

One file, `mxart.py`, Python 3.9+. Only `render --wav` needs numpy.

## What it is for

Each warning code is an entry in a knowledge base: a fault, how often models and composers
commit it, the cases where the warning is wrong, and the sentence that prevents it. The lint is
how an entry is found and how you learn whether it still holds; often the cheapest fix is the
sentence, not the check. `python3 mxart.py explain` lists the entries, including warnings that
were demoted because good music trips them more than weak music does, and findings that have
no check yet.

## Format

```
mxart 1
tempo 112
time 4/4
grid 8                       cells per bar
key C major                  optional: turns on the off-key lint
k 36                         drum palette: one char, then a GM drum note

@track lead program=80 vel=100 range=C4..C6
| E5 -  G5 E5 C5 -  D5 E5 |      a note; '-' holds it; '.' is a rest; C6! is accented
@track pad program=89
| C4+E4+G4 - - - - - - - |       '+' joins a chord
@drums kick
| k...k... | k...k... |          one palette char per cell; several bars on a line is fine
```

Every bar has exactly `grid` cells, so nothing is counted or declared. A row is one voice: a
new note ends the one before it. Two lines that overlap go in two tracks. Lines starting
with `#` are comments.

## Commands

| | |
|---|---|
| `check FILE...` | Every format error at once, each as `file:line: CODE (track, bar, cell): message`. Exit 1 on any. |
| `lint FILE` | Per track: range, most-used pitch, largest leap, where it ends, which bars repeat or transpose which. Then located warnings. `--strict` exits 1 on any. |
| `explain [CODE]` | The knowledge base. For a code: what it means, what was measured on real and model-written music, when it is wrong, and the sentence to put in a brief so it doesn't happen. With no code, every entry and its status. |
| `brief --kind parts` | Those sentences, ready to paste into a composing prompt. |
| `roll FILE` | A text piano roll with bar and beat rulers. `--full` gives a row per semitone. |
| `render FILE -o out.mid [--wav out.wav]` | A type 1 MIDI file, and a plain synth to listen with. |
| `import in.mid -o out.mx --grid N` | MIDI as text. Overlapping notes become extra voices. Says how many notes were off the grid. |
| `cmp A B` | Do two files (`.mx` or `.mid`) hold the same notes? |

Errors: `E_BAR_LENGTH E_BAD_NOTE E_HOLD E_UNKNOWN_KEY E_TRACK_LENGTH E_BAD_OPT E_BAD_ROW
E_BAD_LINE E_HEADER E_GRID E_ORDER E_DUP_TRACK E_DUP_KEY E_NO_TRACKS E_TRACKS E_VERSION`.

Warnings: `W_MONOTONE` (half or more of a track is one pitch), `W_LEAP` (over an octave),
`W_RANGE`, `W_REPEAT`, `W_EMPTY_BAR`, `W_EMPTY_TRACK`.

Part-writing is checked only where you ask for it. A line `@voices soprano alto tenor bass`
(track names, highest first) turns on `W_PARALLEL_5TH` and `W_PARALLEL_8VE` between those
voices. One that follows a note held two beats or more is marked as a likely phrase break.

`lint --harmony` also lists `W_OFF_KEY`, `W_CLASH` (a minor 2nd/9th or major 7th) and
`W_CROSSING`. They are off by default because measured on Bach, Corelli, Haydn,
Saint-Georges, Buxtehude and Hummel they fire constantly, and less on weaker music.

## Try it

```
python3 mxart.py check examples/*.mx
python3 mxart.py lint examples/dull.mx
python3 mxart.py roll examples/tune.mx
python3 mxart.py render examples/tune.mx -o out/tune.mid --wav out/tune.wav
python3 mxart.py import out/tune.mid -o out/back.mx --grid 8
python3 mxart.py cmp examples/tune.mx out/back.mx
python3 -m pytest tests -q
```

## What it doesn't do yet

- Velocity is a track setting plus an accent; `cmp` ignores it, and import keeps only the median.
- One tempo and one time signature per file. No swing, triplets against the grid, pitch bend or controllers.
- The lint thresholds (50% for monotone, an octave for a leap) are guesses, not calibrated on real tunes.
- No harmony lint beyond the key: it doesn't know what chord a bar is on.
