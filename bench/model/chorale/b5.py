import mido

# Chorale 5 in A major
TPQ = 480
BPM = 96
NUM, DEN = 3, 4
KEY = "A"
OUT = "/home/user/mxbench/model/chorale/b5.mid"

VOICES = [
    ("soprano", """A4:2 B4 | C#5:2 D5 | E5 D5 C#5 | B4:3 | E5:2 E5 | F#5:2 E5 | D5 C#5 B4 | A4:3 | F#5:2 E5 | D5:2 C#5 | B4 C#5 B4 | A4:3"""),
    ("alto", """E4:2 E4 | E4:2 F#4 | E4 G#4 A4 | A4 G#4:2 | A4:2 B4 | A4:3 | F#4 E#4:2 | F#4:3 | A4:2 A4 | F#4:2 F#4 | F#4 E4 D4 | C#4:3"""),
    ("tenor", """C#4:2 B3 | A3:2 A3 | A3 B3 A3 | B3:3 | C#4:2 B3 | C#4:3 | B3 G#3:2 | A3:3 | A3:2 A3 | B3:2 A3 | B3 A3 G#3 | A3:3"""),
    ("bass", """A3:2 G#3 | A3 F#3 D3 | C#3 B2 A2 | E3:3 | A3:2 G#3 | F#3:3 | B2 C#3:2 | F#3:3 | D3:2 C#3 | B2:2 A2 | D3 E3 E3 | A2:3"""),
]

STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pitch(name):
    p = STEP[name[0]]
    for ch in name[1:-1]:
        p += 1 if ch == "#" else -1
    return p + 12 * (int(name[-1]) + 1)


mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (vname, text) in enumerate(VOICES):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=vname, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=NUM, denominator=DEN, time=0))
        tr.append(mido.MetaMessage("key_signature", key=KEY, time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for tok in text.replace("|", " ").split():
        if ":" in tok:
            n, d = tok.split(":")
            dur = float(d)
        else:
            n, dur = tok, 1.0
        ticks = int(round(dur * TPQ))
        vel = 80 if ch in (0, 3) else 70
        tr.append(mido.Message("note_on", channel=ch, note=pitch(n), velocity=vel, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch(n), velocity=0, time=ticks))
    tr.append(mido.MetaMessage("end_of_track", time=0))
mid.save(OUT)
