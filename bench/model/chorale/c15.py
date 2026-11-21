import mido

TPQ = 480
Q = TPQ
N = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def p(name):
    return 12 * (int(name[-1]) + 1) + N[name[:-1]]

# (pitch, length in quarter notes); bars separated for readability
soprano = [
    ('G#4',1),('A4',1),('B4',1),   ('C#5',2),('B4',1),
    ('A4',1),('G#4',1),('F#4',1),  ('F#4',3),
    ('G#4',1),('B4',1),('E5',1),   ('D#5',2),('E5',1),
    ('D#5',1),('C#5',2),           ('B4',3),
    ('B4',2),('A4',1),             ('C#5',1),('B4',1),('A4',1),
    ('G#4',1),('F#4',2),           ('E4',3),
]
alto = [
    ('E4',1),('D#4',1),('E4',1),   ('E4',2),('E4',1),
    ('E4',1),('E4',1),('E4',1),    ('E4',1),('D#4',2),
    ('E4',1),('D#4',1),('E4',1),   ('F#4',2),('G#4',1),
    ('F#4',1),('E4',2),            ('D#4',3),
    ('E4',2),('E4',1),             ('E4',1),('E4',1),('F#4',1),
    ('E4',1),('D#4',2),            ('B3',3),
]
tenor = [
    ('B3',1),('B3',1),('B3',1),    ('G#3',1),('A3',1),('B3',1),
    ('C#4',1),('C#4',1),('C#4',1), ('B3',3),
    ('B3',1),('A3',1),('B3',1),    ('B3',2),('B3',1),
    ('B3',1),('A#3',2),            ('B3',2),('A3',1),
    ('G#3',2),('A3',1),            ('G#3',1),('B3',1),('C#4',1),
    ('B3',2),('A3',1),             ('G#3',3),
]
bass = [
    ('E3',1),('F#3',1),('G#3',1),  ('C#3',2),('G#3',1),
    ('A3',1),('C#3',1),('A#2',1),  ('B2',3),
    ('E3',1),('F#3',1),('G#3',1),  ('B2',1),('B3',1),('E3',1),
    ('F#3',2),('F#2',1),           ('B2',3),
    ('E3',1),('D3',1),('C#3',1),   ('C#3',1),('G#3',1),('A3',1),
    ('B3',1),('B2',2),             ('E3',3),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate([('soprano', soprano, 84), ('alto', alto, 70),
                                         ('tenor', tenor, 70), ('bass', bass, 78)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('time_signature', numerator=3, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='E', time=0))
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(80), time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for nm, ln in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p(nm), velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p(nm), velocity=0, time=int(ln * Q)))
    tr.append(mido.MetaMessage('end_of_track', time=0))

mid.save('/home/user/mxbench/model/chorale/c15.mid')
