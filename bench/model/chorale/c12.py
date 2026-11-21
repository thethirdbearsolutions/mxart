import mido

TPQ = 480
# (midi pitch, length in quarter notes); 9 bars of 4/4, C minor
soprano = [(67,1),(72,1),(74,1),(75,1),  (74,1),(72,1),(74,2),
           (70,1),(75,1),(74,1),(72,1),  (70,1),(68,1),(67,2),
           (67,1),(68,1),(70,1),(72,.5),(70,.5),  (68,1),(67,1),(65,2),
           (68,1),(70,1),(72,1),(74,1),  (75,1),(77,1),(75,1),(74,1),  (72,4)]
alto    = [(63,1),(63,1),(67,1),(67,1),  (67,1),(67,.5),(69,.5),(71,2),
           (67,1),(67,1),(67,1),(63,1),  (62,2),(63,2),
           (63,1),(65,1),(65,1),(64,1),  (65,1),(64,1),(60,2),
           (65,1),(67,1),(68,1),(67,1),  (67,1),(65,1),(67,1),(65,1),  (65,1),(64,3)]
tenor   = [(60,1),(60,1),(59,1),(60,1),  (62,1),(63,1),(62,2),
           (58,1),(60,1),(58,1),(60,1),  (53,2),(55,2),
           (60,1),(60,1),(58,1),(55,1),  (60,1),(58,1),(56,2),
           (60,1),(63,1),(63,1),(62,1),  (60,1),(60,1),(60,1),(59,1),  (55,4)]
bass    = [(48,.5),(50,.5),(51,1),(50,1),(48,1),  (47,1),(48,1),(43,2),
           (51,1),(48,1),(43,1),(44,1),  (46,2),(51,2),
           (48,1),(53,.5),(51,.5),(49,1),(48,1),  (44,.5),(46,.5),(48,1),(41,2),
           (53,1),(51,.5),(50,.5),(48,1),(47,1),  (48,.5),(46,.5),(44,1),(43,2),  (48,4)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate([("soprano", soprano, 84), ("alto", alto, 68),
                                         ("tenor", tenor, 68), ("bass", bass, 76)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(66), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Cm', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        t = int(d * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=t))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale/c12.mid')
