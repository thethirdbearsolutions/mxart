import mido

TPQ = 480
N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def p(name):
    letter, rest = name[0], name[1:]
    acc = 0
    if rest[0] == '#':
        acc, rest = 1, rest[1:]
    elif rest[0] == 'b':
        acc, rest = -1, rest[1:]
    return 12 * (int(rest) + 1) + N[letter] + acc

def parse(text):
    out = []
    for tok in text.replace('|', ' ').split():
        name, dur = tok.split(':')
        out.append((name, float(dur)))
    return out

soprano = parse("""
B4:1 E5:1 D5:1 C5:1 | B4:1 A4:1 G4:2 |
G4:1 A4:1 B4:1 C5:.5 B4:.5 | A4:1 F#4:1 G4:2 |
B4:1 C5:1 D5:1 E5:1 | C5:1 B4:1 A4:2 |
C5:1 B4:1 E5:1 D5:.5 C5:.5 | B4:1 A4:1 B4:2 |
E5:1 D5:1 C5:1 A4:1 | G4:1 F#4:1 E4:2
""")
alto = parse("""
E4:1 E4:1 F#4:1 E4:1 | E4:1 D#4:1 E4:2 |
D4:1 D4:1 D4:1 E4:1 | E4:1 D4:.5 C4:.5 B3:2 |
E4:2 E4:1 E4:1 | E4:1 D4:1 C4:2 |
D4:2 E4:1 A4:1 | G4:1 E4:1 D#4:2 |
E4:1 G4:.5 F#4:.5 E4:1 C4:1 | E4:1 D#4:1 B3:2
""")
tenor = parse("""
G3:1 B3:1 A3:2 | G3:.5 A3:.5 B3:1 B3:2 |
B3:1 A3:1 G3:2 | A3:2 G3:2 |
G3:1 A3:1 G#3:1 A3:1 | A3:1 G#3:1 A3:2 |
A3:1 G3:2 F#3:1 | G3:1 F#3:1 B3:2 |
G3:2 A3:.5 G3:.5 F#3:1 | G3:1 A3:1 G#3:2
""")
bass = parse("""
E3:.5 F#3:.5 G3:1 D3:1 A2:1 | B2:2 E3:2 |
G3:1 F#3:1 G3:1 C3:1 | C3:1 D3:1 G2:2 |
E3:1 A2:1 B2:1 C3:1 | E3:1 E2:1 A2:2 |
F#2:1 G2:1 C3:1 D3:1 | E3:.5 D3:.5 C3:1 B2:2 |
C3:1 B2:1 A2:2 | B2:2 E2:2
""")

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [('soprano', soprano, 84), ('alto', alto, 68), ('tenor', tenor, 68), ('bass', bass, 76)]

for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Em', time=0))
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(72), time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    pending = 0
    pos = 0.0
    slowed = False
    for nm, dur in notes:
        if ch == 0 and not slowed and pos >= 36.0:
            # gentle broadening for the final bar
            tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(60), time=pending))
            pending = 0
            slowed = True
        ticks = int(round(dur * TPQ))
        # breathe at phrase ends (long notes closing each two-bar phrase)
        end = pos + dur
        breath = 120 if (end % 8.0 == 0 and dur >= 2 and end < 40) else 0
        tr.append(mido.Message('note_on', channel=ch, note=p(nm), velocity=vel, time=pending))
        tr.append(mido.Message('note_off', channel=ch, note=p(nm), velocity=0, time=ticks - breath))
        pending = breath
        pos = end
    tr.append(mido.MetaMessage('end_of_track', time=pending))

mid.save('/home/user/mxbench/model/chorale/c04.mid')
