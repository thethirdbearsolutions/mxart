import mido

TPQ = 480
# (midi pitch, length in quarter notes); 12 bars of 3/4 in E major
S = [(68,1),(68,1),(69,1), (71,2),(73,1), (71,1),(69,1),(68,1), (66,3),
     (71,1),(73,1),(75,1), (76,2),(73,1), (71,2),(70,1), (71,3),
     (73,1),(71,1),(71,1), (69,1),(73,1),(71,1), (69,1),(68,1),(66,1), (64,3)]
A = [(64,1),(64,1),(64,1), (68,1),(64,1),(64,1), (64,1),(66,1),(64,1), (63,3),
     (64,1),(64,1),(68,1), (64,1),(68,1),(68,1), (66,2),(64,1), (63,3),
     (61,1),(66,1),(64,1), (64,1),(64,1),(64,1), (66,1),(64,1),(63,1), (59,3)]
T = [(59,1),(61,1),(61,1), (59,1),(59,.5),(57,.5),(56,1), (59,1),(61,1),(59,1), (59,2),(57,1),
     (56,1),(56,1),(59,1), (59,1),(59,1),(61,1), (63,2),(61,1), (59,3),
     (57,1),(57,1),(56,1), (57,1),(57,1),(59,1), (61,1),(59,1),(57,1), (56,3)]
B = [(52,.5),(51,.5),(49,1),(45,1), (52,1),(56,1),(49,1), (56,1),(57,1),(59,1), (47,3),
     (52,.5),(51,.5),(49,1),(56,1), (56,.5),(54,.5),(52,1),(52,1), (54,2),(54,1), (47,3),
     (54,1),(51,1),(52,1), (49,1),(45,1),(44,1), (45,1),(47,1),(47,1), (52,3)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano", S), ("alto", A), ("tenor", T), ("bass", B)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(84), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=3, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='E', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=int(d * TPQ)))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d15.mid')
