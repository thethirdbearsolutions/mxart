import mido

TPQ = 480
N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def p(name):
    letter, rest = name[0], name[1:]
    acc = 0
    while rest[0] in '#b':
        acc += 1 if rest[0] == '#' else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + N[letter] + acc


# (note, beats) per voice; bars separated for readability. B minor, 4/4, 10 bars.
soprano = [
    ('B4', 1), ('C#5', 1), ('D5', 1), ('B4', 1),
    ('E5', 1), ('D5', 1), ('C#5', 2),
    ('D5', 1), ('E5', 1), ('F#5', 1), ('E5', 1),
    ('D5', 1), ('C#5', 1), ('D5', 2),
    ('A4', 1), ('B4', 1), ('E5', 1), ('C#5', 1),
    ('D5', 1), ('E5', 1), ('F#5', 2),
    ('F#5', 1), ('E5', 1), ('D5', 1), ('C#5', 1),
    ('D5', 1), ('C#5', 1), ('B4', 2),
    ('B4', 1), ('C#5', 1), ('D5', 1), ('C5', 1),
    ('B4', 1), ('A#4', 1), ('B4', 2),
]
alto = [
    ('D4', 1), ('E4', 1), ('D4', 1), ('D4', 1),
    ('E4', 1), ('F#4', 1), ('F#4', 2),
    ('F#4', 1), ('E4', 1), ('A4', 1), ('G4', 1),
    ('F#4', 1), ('G4', 1), ('F#4', 2),
    ('F#4', 1), ('F#4', 1), ('G4', 1), ('G4', 1),
    ('F#4', 1), ('B4', 1), ('A#4', 2),
    ('B4', 1), ('A#4', 1), ('B4', .5), ('A4', .5), ('G4', 1),
    ('F#4', 1), ('E4', 1), ('D4', 2),
    ('F#4', 1), ('F#4', 1), ('F#4', 1), ('E4', 1),
    ('D4', 1), ('E4', 1), ('D#4', 2),
]
tenor = [
    ('F#3', 1), ('F#3', 1), ('F#3', 1), ('G3', .5), ('A3', .5),
    ('B3', 1), ('B3', 1), ('A#3', 2),
    ('B3', 1), ('A3', 1), ('D4', 1), ('B3', 1),
    ('D4', 1), ('E4', 1), ('D4', 2),
    ('D4', 1), ('B3', 1), ('B3', 1), ('A#3', 1),
    ('B3', 1), ('B3', 1), ('C#4', 2),
    ('D4', 1), ('E4', 1), ('F#4', 1), ('E4', 1),
    ('B3', 1), ('A#3', 1), ('B3', 2),
    ('B3', 1), ('A#3', 1), ('B3', 1), ('G3', 1),
    ('B3', 1), ('C#4', 1), ('B3', 2),
]
bass = [
    ('B2', 1), ('A#2', 1), ('B2', 1), ('G2', 1),
    ('G2', 1), ('F#2', 1), ('F#2', 2),
    ('B2', 1), ('C#3', 1), ('D3', 1), ('G3', 1),
    ('A3', 1), ('A2', 1), ('D3', 2),
    ('D3', 1), ('D#3', 1), ('E3', 1), ('E3', 1),
    ('D3', 1), ('G3', 1), ('F#3', 2),
    ('B2', 1), ('C#3', 1), ('D3', 1), ('E3', 1),
    ('F#3', 1), ('F#2', 1), ('G2', 2),
    ('D3', 1), ('C#3', 1), ('B2', .5), ('D3', .5), ('E3', 1),
    ('F#3', 1), ('F#2', 1), ('B2', 2),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [('soprano', soprano, 84), ('alto', alto, 70),
          ('tenor', tenor, 70), ('bass', bass, 78)]
for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Bm', time=0))
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(68), time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for nm, beats in notes:
        t = int(beats * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=p(nm), velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p(nm), velocity=0, time=t))
    tr.append(mido.MetaMessage('end_of_track', time=0))

mid.save('/home/user/mxbench/model/chorale/c06.mid')
