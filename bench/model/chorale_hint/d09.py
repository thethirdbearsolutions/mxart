import mido

TPQ = 480
# (midi pitch, length in quarter notes); 8 bars of 4/4 in Bb major
soprano = [(70,1),(72,1),(74,1),(75,1), (74,1),(72,1),(72,2),
           (74,1),(70,1),(72,1),(72,1), (74,1),(76,1),(77,2),
           (77,1),(75,1),(74,1),(72,1), (70,1),(69,1),(67,2),
           (70,1),(72,1),(74,1),(75,1), (74,1),(72,1),(70,2)]
alto = [(65,1),(65,1),(65,1),(63,1), (65,1),(67,1),(65,2),
        (65,1),(62,1),(67,1),(65,1), (65,1),(67,1),(69,2),
        (70,1),(67,1),(67,1),(67,1), (67,1),(66,1),(62,2),
        (65,1),(65,1),(65,1),(67,1), (65,1),(63,1),(62,2)]
tenor = [(62,1),(60,1),(58,1),(58,1), (58,1),(58,1),(57,2),
         (58,1),(58,1),(58,1),(57,1), (57,1),(60,1),(60,2),
         (62,1),(58,1),(58,1),(60,1), (62,1),(62,.5),(60,.5),(58,2),
         (58,1),(57,1),(58,1),(58,1), (58,1),(57,1),(58,2)]
bass = [(46,1),(45,1),(46,.5),(45,.5),(43,1), (50,1),(51,1),(53,2),
        (46,.5),(45,.5),(43,1),(52,1),(53,1), (50,1),(48,1),(53,2),
        (46,1),(51,.5),(53,.5),(55,1),(51,1), (50,1),(50,1),(55,2),
        (50,1),(48,1),(46,1),(51,1), (53,1),(41,1),(46,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", soprano), ("alto", alto),
                                    ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Bb', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=int(d * TPQ)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d09.mid')
