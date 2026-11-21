import mido

TPQ = 480
Q, E, H, DH = 480, 240, 960, 1440

# (midi note, duration in ticks) per voice; 12 bars of 3/4 in G major
soprano = [
    (67,Q),(69,Q),(71,Q),  (74,Q),(72,Q),(71,Q),  (69,Q),(71,Q),(72,Q),  (71,Q),(69,H),
    (71,Q),(72,Q),(74,Q),  (76,Q),(74,Q),(76,Q),  (78,Q),(76,H),         (74,DH),
    (74,Q),(72,Q),(71,Q),  (76,Q),(74,Q),(72,Q),  (71,Q),(69,H),         (67,DH),
]
alto = [
    (62,Q),(62,Q),(62,Q),  (62,Q),(64,Q),(64,Q),  (64,Q),(67,Q),(64,Q),  (67,Q),(66,H),
    (67,Q),(67,Q),(66,Q),  (64,Q),(66,Q),(67,Q),  (66,Q),(69,Q),(67,Q),  (66,DH),
    (67,Q),(67,Q),(67,Q),  (67,Q),(67,Q),(69,Q),  (67,Q),(66,H),         (62,DH),
]
tenor = [
    (59,Q),(57,Q),(55,Q),  (55,Q),(55,Q),(55,Q),  (57,Q),(62,Q),(60,Q),  (62,DH),
    (62,Q),(60,Q),(57,Q),  (57,Q),(57,Q),(59,Q),  (62,Q),(61,H),         (62,H),(60,Q),
    (59,Q),(60,Q),(64,Q),  (60,Q),(62,Q),(64,Q),  (62,Q),(62,Q),(60,Q),  (59,DH),
]
bass = [
    (55,Q),(54,Q),(55,Q),  (47,Q),(48,E),(50,E),(52,Q),  (48,Q),(47,Q),(45,Q),  (50,DH),
    (55,Q),(52,Q),(50,Q),  (49,Q),(50,Q),(43,Q),  (45,DH),               (50,DH),
    (55,E),(54,E),(52,E),(54,E),(55,Q),  (48,Q),(47,Q),(48,Q),  (50,DH),  (43,DH),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", soprano), ("alto", alto),
                                    ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(84), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=3, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='G', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for n, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=n, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=n, velocity=0, time=d))
    tr.append(mido.MetaMessage('end_of_track', time=0))

mid.save('/home/user/mxbench/model/chorale_hint/d03.mid')
