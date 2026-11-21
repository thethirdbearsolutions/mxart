import mido

Q = 480
# (midi note, length in quarter notes) per voice; 8 bars of 4/4, F# minor
soprano = [(66,1),(68,1),(69,1),(71,1), (73,1),(71,1),(69,2),
           (69,1),(71,1),(73,1),(76,1), (74,.5),(73,.5),(71,1),(69,2),
           (73,1),(74,1),(73,1),(71,1), (69,1),(71,1),(73,2),
           (76,1),(74,1),(73,1),(71,1), (69,1),(68,1),(66,2)]
alto    = [(61,1),(61,1),(61,1),(62,1), (66,1),(65,1),(66,2),
           (64,1),(64,1),(64,1),(64,1), (66,1),(68,1),(64,2),
           (69,1),(66,1),(66,1),(68,1), (66,1),(66,1),(65,2),
           (64,1),(66,1),(66,1),(66,1), (66,1),(65,1),(61,2)]
tenor   = [(57,1),(59,1),(57,1),(56,1), (57,1),(56,1),(57,2),
           (61,1),(62,1),(61,1),(57,1), (62,1),(62,1),(61,2),
           (61,1),(59,1),(57,1),(61,1), (61,1),(59,1),(56,2),
           (61,.5),(59,.5),(57,1),(57,1),(62,1), (61,1),(59,1),(58,2)]
bass    = [(54,1),(53,1),(54,1),(47,1), (45,.5),(47,.5),(49,1),(54,2),
           (57,1),(56,1),(57,1),(49,1), (47,1),(52,1),(45,2),
           (54,1),(50,1),(54,1),(53,1), (54,.5),(52,.5),(50,1),(49,2),
           (45,1),(50,1),(45,1),(47,1), (49,1),(49,1),(42,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=Q)
for ch, (name, notes) in enumerate([("soprano", soprano), ("alto", alto),
                                    ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(69), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='F#m', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for n, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=n, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=n, velocity=0, time=int(d * Q)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d14.mid')
