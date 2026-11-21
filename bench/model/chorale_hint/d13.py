import mido

TPQ = 480
# (midi pitch, length in quarter notes), 8 bars of 4/4 in A major
S = [(69,1),(69,1),(71,1),(73,1), (74,1),(73,1),(71,2), (76,1),(78,1),(76,1),(73,1), (71,1),(69,1),(68,2),
     (69,1),(71,1),(73,1),(74,1), (73,1),(71,1),(69,2), (73,1),(78,1),(76,1),(74,1), (73,1),(71,1),(69,2)]
A = [(64,1),(66,1),(64,1),(69,1), (69,1),(69,1),(69,1),(68,1), (69,1),(69,1),(69,1),(69,.5),(68,.5), (66,1),(66,1),(64,2),
     (64,1),(64,1),(64,1),(62,1), (66,1),(65,1),(66,2), (64,1),(66,1),(69,1),(71,1), (69,1),(68,1),(64,2)]
T = [(61,1),(61,1),(64,1),(64,1), (62,1),(64,1),(64,2), (64,1),(62,1),(64,1),(66,1), (66,1),(63,1),(59,2),
     (57,1),(56,1),(57,.5),(56,.5),(54,1), (57,1),(56,1),(57,2), (57,1),(57,1),(64,1),(66,1), (64,1),(64,.5),(62,.5),(61,2)]
B = [(57,.5),(56,.5),(54,1),(56,1),(57,1), (54,1),(57,1),(52,2), (49,1),(50,1),(49,1),(54,1), (51,1),(47,1),(52,2),
     (49,1),(47,1),(45,1),(47,1), (49,1),(49,1),(54,2), (57,1),(50,1),(49,1),(50,1), (52,1),(52,1),(45,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", S), ("alto", A), ("tenor", T), ("bass", B)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='A', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=80, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=int(d * TPQ)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d13.mid')
