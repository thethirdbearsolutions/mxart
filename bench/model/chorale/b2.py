import mido

# Chorale 2 in E minor
TPQ = 480
BPM = 72
NUM, DEN = 4, 4
KEY = "Em"
OUT = "/home/user/mxbench/model/chorale/b2.mid"

VOICES = [
    ("soprano", """B4 B4 E5 D5 | C5:.5 B4:.5 A4 B4:2 | G4 A4 B4 D5 | B4 A4 G4:2 | B4 C5 D5 E5 | D5:2 C5:2 | C5 B4 A4 G4 | A4 G4:.5 F#4:.5 E4:2"""),
    ("alto", """E4 F#4 G4 G4 | E4 E4 D#4:2 | E4 F#4 G4 A4 | G4 F#4 D4:2 | G4 F#4 G4 G4 | F4 E4 E4:2 | E4 E4 F#4 E4 | E4 E4:.5 D#4:.5 B3:2"""),
    ("tenor", """G3 F#3 B3 B3 | G3 A3 F#3:2 | B3 D4 D4 C4 | B3 A3:.5 C4:.5 B3:2 | D4 D4 D4 C4 | A3 G#3 A3:2 | A3 G3 B3 B3 | A3 B3 G#3:2"""),
    ("bass", """E3 D#3 E3 G3 | C3 C3 B2:2 | E3 D3 G3 F#3 | G3 D3 G2:2 | G3 A3 B3 C4 | F3 E3 A2:2 | C3 E3 D#3 E3 | C3 B2 E2:2"""),
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
