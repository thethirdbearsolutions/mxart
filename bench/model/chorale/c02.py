import mido

TPQ = 480
N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def p(name):
    letter, rest = name[0], name[1:]
    acc = 0
    if rest[0] == '#':
        acc, rest = 1, rest[1:]
    return 12 * (int(rest) + 1) + N[letter] + acc

# (note, length in quarter notes), bar by bar
soprano = [
    ('A4', 1), ('C5', 1), ('B4', 1), ('A4', 1),
    ('D5', 1), ('C5', 1), ('B4', 2),
    ('C5', 1), ('D5', 1), ('E5', 1), ('F5', 1),
    ('E5', 1), ('D5', 1), ('C5', 2),
    ('C5', 1), ('E5', 1), ('D5', 1), ('B4', 1),
    ('C5', 1), ('D5', 1), ('E5', 2),
    ('E5', 1), ('F5', 1), ('E5', 1), ('D5', 1),
    ('C5', 1), ('B4', 1), ('A4', 2),
]
alto = [
    ('C4', 1), ('E4', 1), ('E4', 1), ('E4', 1),
    ('D4', 1), ('E4', 1), ('E4', 2),
    ('E4', 1), ('G4', 1), ('G4', 1), ('A4', 1),
    ('G4', 1), ('F4', 1), ('E4', 2),
    ('A4', 1), ('A4', 1), ('A4', 1), ('G#4', 1),
    ('A4', 1), ('A4', 1), ('G#4', 2),
    ('A4', 1), ('A4', 1), ('A4', 1), ('B4', 1),
    ('A4', 1), ('G#4', 1), ('E4', 2),
]
tenor = [
    ('E3', 1), ('A3', 1), ('B3', 1), ('C4', .5), ('B3', .5),
    ('A3', 1), ('A3', 1), ('G#3', 2),
    ('G3', 1), ('D4', 1), ('C4', 1), ('C4', 1),
    ('C4', 1), ('B3', 1), ('C4', 2),
    ('E4', 1), ('E4', 1), ('F4', 1), ('E4', 1),
    ('E4', 1), ('D4', 1), ('B3', 2),
    ('C4', 1), ('C4', .5), ('D4', .5), ('E4', 1), ('F4', 1),
    ('E4', 1), ('E4', .5), ('D4', .5), ('C4', 2),
]
bass = [
    ('A2', .5), ('B2', .5), ('C3', 1), ('G#2', 1), ('A2', 1),
    ('F2', 1), ('E2', 1), ('E2', 2),
    ('C3', 1), ('B2', 1), ('C3', 1), ('F3', 1),
    ('G3', 1), ('G2', 1), ('C3', 2),
    ('C3', 1), ('C#3', 1), ('D3', 1), ('D3', 1),
    ('C3', 1), ('F3', 1), ('E3', 2),
    ('A3', 1), ('F3', .5), ('D3', .5), ('C3', 1), ('D3', 1),
    ('E3', 1), ('E2', 1), ('A2', 2),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [('soprano', soprano, 76), ('alto', alto, 64), ('tenor', tenor, 64), ('bass', bass, 72)]
for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Am', time=0))
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(72), time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for n, d in notes:
        t = int(d * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=p(n), velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p(n), velocity=0, time=t))
    tr.append(mido.MetaMessage('end_of_track', time=0))

mid.save('/home/user/mxbench/model/chorale/c02.mid')
