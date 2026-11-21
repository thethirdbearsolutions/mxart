import mido

TPQ = 480
Q, E, H = 480, 240, 960

N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def p(name):
    letter, rest = name[0], name[1:]
    acc = 0
    while rest[0] in 'b#':
        acc += -1 if rest[0] == 'b' else 1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + N[letter] + acc

def v(s):
    out = []
    for tok in s.split():
        n, d = tok.split(':')
        out.append((p(n), {'q': Q, 'e': E, 'h': H}[d]))
    return out

soprano = v(
    "G4:q Ab4:q Bb4:q Eb5:q | D5:q C5:q Bb4:h | "
    "Bb4:q C5:q D5:q Eb5:e D5:e | C5:q B4:q C5:h | "
    "Eb5:q F5:q Eb5:e C5:e Bb4:q | C5:q Eb5:q D5:h | "
    "Bb4:q Ab4:q G4:q Ab4:q | G4:q F4:q Eb4:h".replace('|', ''))
alto = v(
    "Eb4:q D4:q Eb4:q Eb4:q | F4:q Eb4:q D4:h | "
    "Eb4:q Eb4:q F4:q Eb4:q | F4:q G4:q G4:h | "
    "Bb4:q Bb4:q G4:q G4:q | F4:q F4:q F4:h | "
    "G4:q D4:q Eb4:q F4:q | Eb4:q D4:q Bb3:h".replace('|', ''))
tenor = v(
    "Bb3:q Bb3:q Bb3:e Ab3:e G3:q | Bb3:q A3:q Bb3:h | "
    "G3:q G3:q Ab3:q Bb3:q | C4:q D4:q Eb4:h | "
    "Eb4:q D4:q Eb4:q Eb4:q | Eb4:q C4:q Bb3:h | "
    "Bb3:q Bb3:q Bb3:q C4:q | Bb3:q Bb3:e Ab3:e G3:h".replace('|', ''))
bass = v(
    "Eb3:q F3:q G3:q C3:q | Bb2:q F3:q Bb2:h | "
    "Eb3:q C3:q F3:q G3:q | Ab3:q G3:q C3:h | "
    "G3:q Bb3:q C4:q G3:q | Ab3:q A3:q Bb3:h | "
    "Eb3:q F3:q Eb3:q Ab2:q | Bb2:q Bb2:q Eb3:h".replace('|', ''))

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate([
        ('soprano', soprano, 84), ('alto', alto, 70),
        ('tenor', tenor, 70), ('bass', bass, 78)]):
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Eb', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for pitch, dur in notes:
        tr.append(mido.Message('note_on', channel=ch, note=pitch, velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=pitch, velocity=0, time=dur))
    tr.append(mido.MetaMessage('end_of_track', time=0))
    mid.tracks.append(tr)

mid.save('/home/user/mxbench/model/chorale/c11.mid')
