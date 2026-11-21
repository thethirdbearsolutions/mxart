import mido

TPQ = 480
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEY, NUM, DEN, BPM = 'C', 4, 4, 80

VOICES = {
    'soprano': "E4 G4 C5 B4 | A4 A4 G4:2 | G4 C5 B4 A4 | B4 A4 G4:2 | E5 D5 C5 A4 | C5 B4 A4:2 | F5 E5 D5 C5 | D5 B4 C5:2",
    'alto':    "C4 D4 E4 D4 | C4 C4 B3:2 | E4 E4 E4 C4 | B3 C4 B3:2 | G4 G4 E4 D4 | E4 D4 C4:2 | A4 G4 G4 A4 | A4 G4:.5 F4:.5 E4:2",
    'tenor':   "G3 G3 G3 G3 | E3 D3 D3:2 | G3 A3 G3 E3 | G3 F#3 G3:2 | G3 G3 A3 A3 | A3 G#3 A3:2 | C4 C4 D4 E4 | D4 D4 C4:2",
    'bass':    "C3 B2 C3 G2 | A2 F#2 G2:2 | C3:.5 B2:.5 A2 E3 C3 | D3 D3 G2:2 | C3 B2 A2 F3 | E3 E3 A2:2 | F3 C3 B2 A2 | F3 G3 C3:2",
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
