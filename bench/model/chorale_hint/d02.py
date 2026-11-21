import mido

TPQ = 480
# (midi pitch, length in quarter notes), 8 bars of 4/4 in A minor
S = [(69,1),(71,1),(72,1),(74,1), (76,1),(74,1),(71,2),
     (72,1),(74,1),(76,1),(77,1), (76,1),(74,1),(72,2),
     (76,1),(77,1),(74,1),(76,.5),(74,.5), (72,1),(74,1),(76,2),
     (76,1),(74,1),(72,1),(74,1), (72,1),(71,1),(69,2)]
A = [(64,1),(64,1),(64,1),(65,1), (64,1),(65,1),(64,2),
     (64,1),(67,1),(67,1),(69,1), (67,1),(65,1),(64,2),
     (67,1),(65,1),(65,1),(64,1), (64,1),(62,1),(59,2),
     (60,1),(62,1),(64,1),(69,1), (69,1),(68,1),(64,2)]
T = [(60,1),(59,1),(57,1),(57,1), (57,1),(59,.5),(57,.5),(56,2),
     (57,1),(55,1),(60,1),(60,1), (60,1),(59,1),(55,2),
     (57,1),(57,1),(55,1),(55,1), (57,1),(57,2),(56,1),
     (57,1),(56,1),(57,1),(57,1), (57,1),(59,.5),(62,.5),(61,2)]
B = [(45,1),(44,1),(45,1),(50,1), (48,1),(50,1),(52,2),
     (45,1),(47,1),(48,1),(53,1), (55,1),(43,1),(48,2),
     (49,1),(50,.5),(48,.5),(47,1),(48,.5),(47,.5), (45,1),(53,1),(52,2),
     (45,1),(47,1),(48,1),(53,1), (52,1),(52,1),(45,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", S), ("alto", A), ("tenor", T), ("bass", B)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(66), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Am', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=78, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=int(d * TPQ)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d02.mid')
