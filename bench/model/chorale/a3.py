import mido

TPQ = 480
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEY, NUM, DEN, BPM = 'Dm', 4, 4, 72

VOICES = {
    'soprano': "A4 D5 C#5 D5 | E5 F5 E5:2 | C5 D5 C5 Bb4 | A4 G4 F4:2 | A4 Bb4 C5 D5 | Bb4 A4 G4:2 | D5 C5 Bb4 A4 | G4 F4 E4:2 | A4 Bb4 A4 G4 | F4 E4 D4:2",
    'alto':    "F4 D4 E4 F4 | G4 F4 A4:2 | A4 F4 F4 G4 | F4 E4 C4:2 | F4 F4 G4 A4 | G4 F#4 D4:2 | F4 F4 G4 F4 | E4 D4 C#4:2 | F4 D4 D4 C#4 | D4 C#4 A3:2",
    'tenor':   "A3 A3 G3 A3 | A3 A3 C#4:2 | C4 Bb3 C4 D4 | C4 Bb3 A3:2 | C4 D4 C4 A3 | D4 D4:.5 C4:.5 Bb3:2 | Bb3 C4 D4 D4:.5 C4:.5 | Bb3 A3 A3:2 | A3 G3 A3 A3 | A3 A3:.5 G3:.5 F#3:2",
    'bass':    "D3 F3 E3 D3 | C#3 D3 A2:2 | F3 Bb2 A2 Bb2 | C3 C3 F3:2 | F3:.5 E3:.5 D3 E3 F#3 | G3 D3 G2:2 | Bb2 A2 G2 D3 | G2 A2 A2:2 | D3 G3 F3 E3 | D3 A2 D3:2",
}


def pitch(name):
    letter, rest = name[0], name[1:]
    acc = 0
    while rest[0] in '#b':
        acc += 1 if rest[0] == '#' else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + NOTE[letter] + acc


def parse(text):
    out = []
    for tok in text.replace('|', ' ').split():
        if ':' in tok:
            n, d = tok.split(':')
            d = float(d)
        else:
            n, d = tok, 1.0
        out.append((pitch(n), int(round(d * TPQ))))
    return out


mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, name in enumerate(['soprano', 'alto', 'tenor', 'bass']):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=NUM, denominator=DEN, time=0))
        tr.append(mido.MetaMessage('key_signature', key=KEY, time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in parse(VOICES[name]):
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=d))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save(__file__[:-3] + '.mid')
