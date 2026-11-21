import mido

# Chorale 1 in B-flat major
TPQ = 480
BPM = 76
NUM, DEN = 4, 4
KEY = "Bb"
OUT = "/home/user/mxbench/model/chorale/b1.mid"

VOICES = [
    ("soprano", """Bb4 C5 D5 D5 | Eb5 D5 C5:2 | D5 Eb5 F5:.5 Eb5:.5 D5 | Bb4 C5 D5:2 | D5:.5 Eb5:.5 F5 G5 F5 | Eb5 C5 D5:2 | Bb4 Eb5 D5 C5 | Bb4 A4 Bb4:2"""),
    ("alto", """F4 F4 G4 F4 | G4 G4 G4 A4 | F4 G4 F4 F4 | G4 G4 F#4:2 | G4 Bb4 Bb4 C5 | Bb4 A4 F4:2 | D4 G4 Bb4 G4 | F4 F4:.5 Eb4:.5 D4:2"""),
    ("tenor", """D4 C4 Bb3 Bb3 | Bb3 Bb3 C4 C4 | Bb3 Bb3 Bb3 Bb3 | D4 C4 A3:2 | Bb3 Bb3 Bb3 A3 | Bb3 C4 Bb3:2 | Bb3 C4 F4 Eb4 | D4 C4 Bb3:2"""),
    ("bass", """Bb3 A3 G3 Bb3 | Eb3:.5 F3:.5 G3 E3 F3 | Bb3 Eb3 D3 Bb3 | G3:.5 F3:.5 Eb3 D3:2 | G3 D3 Eb3 F3 | G3 F3 Bb3:2 | G3 C3 D3 Eb3 | F3 F3 Bb2:2"""),
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
