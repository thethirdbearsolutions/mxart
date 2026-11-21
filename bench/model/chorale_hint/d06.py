import mido

TPQ = 480
# (midi pitch, length in quarter notes); 8 bars of 4/4, B minor
soprano = [(71,1),(73,1),(74,1),(71,1), (76,1),(74,1),(73,2),
           (74,1),(73,1),(74,1),(76,1), (78,1),(76,1),(74,2),
           (78,1),(79,1),(78,1),(76,1), (74,1),(76,1),(78,2),
           (74,1),(76,1),(78,1),(76,1), (74,1),(73,1),(71,2)]
alto    = [(66,1),(66,1),(66,1),(67,1), (67,1),(66,1),(66,2),
           (66,1),(69,1),(69,1),(69,1), (69,1),(67,1),(66,2),
           (71,1),(71,1),(71,1),(70,1), (71,1),(71,1),(70,2),
           (71,1),(71,1),(71,1),(67,1), (62,1),(64,1),(63,2)]
tenor   = [(62,1),(64,1),(62,1),(62,1), (64,1),(59,1),(58,2),
           (59,1),(64,1),(62,.5),(59,.5),(57,1), (62,1),(64,.5),(61,.5),(62,2),
           (62,1),(64,1),(66,1),(66,1), (66,1),(64,1),(61,2),
           (62,1),(59,1),(62,1),(61,1), (59,1),(58,1),(54,2)]
bass    = [(59,1),(58,1),(59,.5),(57,.5),(55,1), (52,1),(54,1),(54,2),
           (59,1),(57,1),(54,1),(49,1), (50,1),(55,.5),(57,.5),(50,2),
           (47,1),(52,1),(50,1),(49,1), (50,.5),(52,.5),(55,1),(54,2),
           (59,.5),(57,.5),(55,1),(59,1),(52,1), (54,1),(54,1),(47,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", soprano), ("alto", alto),
                                    ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(66), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='Bm', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for pitch, beats in notes:
        tr.append(mido.Message('note_on', channel=ch, note=pitch, velocity=72, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=pitch, velocity=0, time=int(beats * TPQ)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d06.mid')
