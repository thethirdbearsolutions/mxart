import mido

TPQ = 480
# (midi pitch, length in quarter notes); 10 bars of 4/4, E minor
soprano = [(71,1),(76,1),(74,1),(72,1), (71,1),(69,1),(66,2),
           (67,1),(69,1),(71,.5),(72,.5),(74,1), (72,1),(71,.5),(69,.5),(67,2),
           (71,1),(72,1),(74,1),(76,1), (72,.5),(71,.5),(69,1),(71,2),
           (76,1),(74,1),(72,1),(71,1), (69,2),(67,2),
           (67,1),(72,1),(71,1),(69,1), (67,1),(66,1),(64,2)]
alto = [(67,2),(69,2), (67,1),(64,1),(63,2),
        (64,1),(62,1),(62,2), (64,1),(62,.5),(60,.5),(59,2),
        (64,1),(64,1),(62,1),(62,1), (60,1),(64,2),(63,1),
        (64,1),(69,1),(64,1),(64,1), (64,1),(66,1),(64,2),
        (64,1),(64,1),(64,1),(66,1), (64,1),(63,1),(59,2)]
tenor = [(64,1),(59,1),(57,1),(62,1), (62,1),(60,1),(59,2),
         (59,1),(57,1),(55,1),(55,1), (55,1),(55,.5),(54,.5),(55,2),
         (55,1),(55,1),(55,1),(56,1), (57,1),(57,1),(59,2),
         (59,1),(57,1),(55,1),(59,1), (60,1),(59,1),(59,2),
         (55,1),(57,1),(59,1),(60,1), (59,1),(57,1),(56,2)]
bass = [(52,.5),(54,.5),(55,1),(54,1),(54,1), (55,1),(57,1),(59,1),(47,1),
        (52,1),(54,1),(55,1),(47,1), (48,1),(50,1),(43,2),
        (52,1),(48,1),(47,1),(52,1), (45,1),(48,1),(47,2),
        (55,1),(54,1),(52,1),(55,1), (57,1),(51,1),(52,1),(50,1),
        (48,.5),(47,.5),(45,1),(43,1),(45,1), (47,1),(47,1),(40,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", soprano), ("alto", alto),
                                    ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(72), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Em', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        t = int(d * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=80, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=t))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d04.mid')
