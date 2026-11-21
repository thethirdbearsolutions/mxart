import mido

TPQ = 480
# (midi pitch, length in quarter notes); 8 bars of 3/4 in D minor
S = [(69,1),(74,1),(73,1), (74,2),(76,1), (77,1),(76,1),(74,1), (73,3),
     (69,1),(72,1),(77,1), (76,1),(74,1),(72,1), (74,1),(76,1),(73,1), (74,3)]
A = [(62,1),(62,1),(64,1), (65,1),(67,1),(67,1), (65,1),(67,1),(67,1), (64,3),
     (65,1),(65,1),(65,1), (67,1),(65,1),(65,1), (62,1),(67,1),(67,1), (66,3)]
T = [(53,1),(53,1),(57,1), (57,1),(58,1),(57,1), (57,1),(60,1),(62,1), (57,3),
     (60,1),(60,1),(58,1), (55,1),(57,1),(60,1), (55,.5),(57,.5),(58,1),(57,1), (57,3)]
B = [(50,1),(46,1),(45,1), (50,2),(49,1), (50,1),(48,1),(46,1), (45,3),
     (53,.5),(55,.5),(57,1),(50,1), (48,1),(53,1),(45,1), (46,1),(43,1),(45,1), (50,3)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", S), ("alto", A), ("tenor", T), ("bass", B)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=3, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Dm', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=int(d * TPQ)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d08.mid')
