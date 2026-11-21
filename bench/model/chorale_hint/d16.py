import mido

TPQ = 480
Q, H, W, E, DQ = 480, 960, 1920, 240, 720

# (pitch, duration) per voice; 9 bars of 4/4 in F minor
soprano = [
    (72,Q),(72,Q),(73,Q),(72,Q),
    (70,Q),(68,Q),(67,H),
    (68,Q),(70,Q),(72,Q),(73,Q),
    (72,Q),(70,Q),(68,H),
    (72,Q),(73,Q),(75,Q),(77,Q),
    (75,Q),(73,Q),(72,H),
    (72,Q),(77,Q),(75,Q),(73,Q),
    (72,Q),(70,Q),(68,Q),(67,Q),
    (65,W),
]
alto = [
    (65,Q),(67,Q),(65,Q),(65,Q),
    (65,Q),(65,Q),(64,H),
    (65,Q),(63,Q),(63,Q),(65,Q),
    (63,Q),(67,Q),(63,H),
    (68,Q),(65,Q),(68,Q),(68,Q),
    (63,Q),(65,Q),(64,H),
    (65,Q),(65,Q),(68,Q),(65,Q),
    (65,Q),(64,Q),(65,Q),(64,Q),
    (60,W),
]
tenor = [
    (56,Q),(55,Q),(56,Q),(60,Q),
    (61,Q),(60,Q),(60,H),
    (60,Q),(58,Q),(56,Q),(56,Q),
    (60,Q),(61,Q),(60,H),
    (60,Q),(58,Q),(63,Q),(61,Q),
    (56,Q),(55,Q),(55,H),
    (56,Q),(56,Q),(56,Q),(58,Q),
    (56,Q),(55,Q),(56,Q),(58,Q),
    (57,W),
]
bass = [
    (53,Q),(52,Q),(53,E),(55,E),(56,Q),
    (58,Q),(53,Q),(48,H),
    (53,Q),(55,Q),(56,E),(55,E),(53,Q),
    (56,Q),(51,Q),(56,DQ),(55,E),
    (53,Q),(58,Q),(60,Q),(53,Q),
    (48,Q),(46,Q),(48,H),
    (53,Q),(49,Q),(48,Q),(46,Q),
    (48,Q),(48,Q),(53,Q),(48,Q),
    (41,W),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate(
        [("soprano", soprano), ("alto", alto), ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(66), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Fm', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    vel = 78 if ch == 0 else 68
    for p, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=d))
    tr.append(mido.MetaMessage('end_of_track', time=0))

mid.save('/home/user/mxbench/model/chorale_hint/d16.mid')
