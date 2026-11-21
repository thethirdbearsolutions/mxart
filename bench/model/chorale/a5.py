import mido

TPQ = 480
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEY, NUM, DEN, BPM = 'F', 3, 4, 96

VOICES = {
    'soprano': "F4:2 A4 | C5:2 D5 | C5 Bb4 A4 | G4:3 | A4:2 Bb4 | C5:2 D5 | F5:2 E5 | D5:3 | D5:2 Bb4 | C5:2 A4 | Bb4 A4 G4 | F4:3",
    'alto':    "C4:2 F4 | F4:2 F4 | F4 G4 F4 | F4 E4:2 | F4:2 F4 | G4 A4 G4 | A4:2 G4 | F4:3 | F4:2 G4 | F4:2 F4 | G4 F4 E4 | C4:3",
    'tenor':   "A3:2 A3 | A3:2 Bb3 | A3 C4 C4 | C4:3 | C4:2 D4 | C4:2 Bb3 | D4:2 C#4 | D4:3 | D4:2 D4 | C4:2 D4 | D4 C4 Bb3 | A3:3",
    'bass':    "F3 E3 D3 | F3:2 Bb2 | F3 E3 F3 | C3:3 | F3:2 D3 | E3 F3 Bb2 | A2:2 A2 | D3:2 C3 | Bb2:2 G2 | A2:2 D3 | Bb2 C3 C3 | F2:3",
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
