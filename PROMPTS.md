# The prompts, as sent

Every agent was a fresh session with no knowledge of mxart or of what would be measured.
`{...}` marks the parts that varied.

## Composing a chorale (26 without the sentence, 16 with it)

> You are composing music as a MIDI file. Write one short four-part chorale (soprano, alto, tenor, bass), in the manner of a traditional hymn harmonisation. Make it the best piece of music you can. **Avoid parallel fifths and parallel octaves between voices.**
>
> Write a small Python script that uses the `mido` library (already installed) to produce the MIDI file, then run it. Rules:
> - Output: {path}.mid, with the script beside it.
> - Key and metre: {key}, {metre}.
> - Type 1 MIDI, 480 ticks per quarter note, one track per voice named soprano, alto, tenor, bass (in that order), each on its own channel (0-3). Include a tempo and a time-signature meta message.
> - Length 8 to 12 full bars. Start on the downbeat of bar 1 (no pickup). Shortest note value is a sixteenth; no triplets. Notes within one voice must not overlap.
> - Do not use any music-analysis or music-theory library (no music21, pretty_midi analysis, etc.), and do not write code that checks or analyses the music. Just compose it and write the notes out. You cannot listen to it.
> - Do not read any other files under /home/user.

The sentence in bold is the only difference between `bench/model/chorale/c01..c16` (without)
and `bench/model/chorale_hint/d01..d16` (with). Keys and metres are the same, in the same order.
`a1..a5` and `b1..b5` came from two agents asked for five chorales each, with the same rules.

The folk melodies (`bench/model/folk`) used the same rules for one track named melody, 12 to 16
bars, "in the manner of a traditional European folk song", five per agent.

## Repair, arm A: mxart with its lint

> Work only inside {dir}. It holds piece.mx, a four-part chorale written as text, the tool mxart.py, and README.md describing the format and commands.
>
> Run `python3 mxart.py lint piece.mx`. Fix every parallel fifth and parallel octave it reports between voices, except ones it marks as following a held note (those are fine). Change as few notes as you can, leave the soprano alone if at all possible, keep the length, key and track names, and do not introduce new faults. Edit piece.mx in place. When you finish, `python3 mxart.py check piece.mx` must pass and the lint should report no such parallels.
>
> Use only mxart.py to examine the music; do not write analysis code of your own.

## Repair, arm B: the same text, no lint

> Work only inside {dir}. It holds piece.mx, a four-part chorale written as text, the tool mx.py (commands: check, roll, render), and README.md describing the format.
>
> The chorale may contain part-writing faults: parallel fifths or parallel octaves, where two voices a perfect fifth (or an octave or unison) apart both move in the same direction to another perfect fifth (or octave or unison). One that comes straight after a note held two beats or more is a phrase break and is fine. Find any others and fix them. Change as few notes as you can, leave the soprano alone if at all possible, keep the length, key and track names, and do not introduce new faults. Edit piece.mx in place. When you finish, `python3 mx.py check piece.mx` must pass.
>
> Read the music yourself (the text, and `python3 mx.py roll piece.mx`); do not write analysis or checking code.

`mx.py` is `repair/mx_nolint.py`: mxart with the lint removed.

## Repair, arm C: plain Python

> Work only inside {dir}. It holds piece.mid, a four-part chorale: a type 1 MIDI file with one track per voice, named soprano, alto, tenor, bass.
>
> (the same description of the faults as arm B) Change as few notes as you can, leave the soprano alone if at all possible, keep the length, key, tempo, time signature, track names and channels, and do not introduce new faults.
>
> Use Python however you like (mido is installed), including writing your own code to inspect or check the music. Write the result as fixed.mid in the same directory, with the same structure as piece.mid.
