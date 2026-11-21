import mido

TPQ = 480
# (midi pitch, length in quarter notes), 8 bars of 4/4 in F major
soprano = [(69,1),(70,1),(72,1),(69,1), (70,1),(69,1),(67,2),
           (67,1),(69,1),(70,1),(72,1), (74,1),(71,1),(72,2),
           (72,1),(70,1),(69,1),(74,1), (74,1.5),(73,.5),(74,2),
           (77,1),(74,1),(72,1),(70,1), (69,1),(67,1),(65,2)]
alto = [(65,1),(64,1),(65,1),(65,1), (65,1),(65,1),(64,2),
        (64,1),(65,1),(67,1),(67,1), (65,1),(65,1),(64,2),
        (65,1),(67,1),(65,1),(69,1), (67,1),(64,1),(65,2),
        (65,1),(67,1),(65,1),(67,1), (65,1),(64,1),(60,2)]
tenor = [(60,1),(60,1),(60,1),(62,1), (62,1),(60,1),(60,2),
         (60,1),(60,1),(62,1),(60,1), (57,1),(62,1),(60,2),
         (57,.5),(58,.5),(60,1),(60,1),(60,1), (58,1),(57,1),(57,2),
         (58,1),(58,1),(60,1),(62,1), (60,1),(60,.5),(58,.5),(57,2)]
bass = [(53,1),(55,1),(57,1),(50,1), (46,1),(48,1),(48,2),
        (60,1),(57,1),(55,.5),(53,.5),(52,1), (53,1),(55,1),(48,2),
        (53,1),(52,1),(53,1),(54,1), (55,1),(57,1),(50,2),
        (50,1),(55,1),(57,1),(58,1), (60,1),(48,1),(53,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate([("soprano", soprano, 84), ("alto", alto, 68),
                                         ("tenor", tenor, 70), ("bass", bass, 78)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(72), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='F', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        t = int(d * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=t))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale/c07.mid')
