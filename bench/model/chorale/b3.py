import mido

# Chorale 3 in G minor
TPQ = 480
BPM = 69
NUM, DEN = 4, 4
KEY = "Gm"
OUT = "/home/user/mxbench/model/chorale/b3.mid"

VOICES = [
    ("soprano", """G4:2 A4 Bb4 | C5:.5 Bb4:.5 A4 Bb4:2 | D5:2 C5 D5 | Bb4 G4 A4:2 | Bb4:2 C5 D5 | Eb5 D5 C5:2 | Eb5:2 D5 C5 | Bb4 A4 G4:2"""),
    ("alto", """D4 Eb4 D4 D4 | Eb4 Eb4 D4:2 | F4:2 A4 F4 | D4 C4 A3:2 | D4 D4 Eb4 F4 | Eb4 F4 Eb4:2 | G4 G4 G4 A4 | G4 F#4 D4:2"""),
    ("tenor", """Bb3 Bb3 A3 G3 | G3 C4 Bb3:2 | Bb3:2 C4 Bb3 | Bb3 G3 F#3:2 | G3 G3 G3 B3 | C4 B3 C4:2 | Bb3 C4 D4 Eb4 | D4 C4 Bb3:2"""),
    ("bass", """G3 G3 F#3 G3 | Eb3 F3 Bb2:2 | Bb2 D3 F3 Bb3 | G3:.5 F3:.5 Eb3 D3:2 | G3 F3 Eb3 D3 | C3 G3 C3:2 | Eb3 C3 Bb2 C3 | D3 D3 G2:2"""),
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
