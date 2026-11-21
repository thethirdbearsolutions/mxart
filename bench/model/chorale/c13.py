import mido

TPQ = 480
# (midi note, length in quarter notes); 10 bars of 4/4, A major
S = [(69,1),(71,1),(73,1),(74,1),  (76,1),(74,.5),(73,.5),(71,2),
     (73,1),(76,1),(78,1),(78,1),  (76,1),(75,1),(76,2),
     (76,1),(74,1),(73,1),(71,1),  (69,1),(68,1),(69,2),
     (69,1),(71,1),(73,1),(74,1),  (76,1),(78,1),(76,2),
     (73,1),(78,1),(76,1),(74,1),  (73,1),(71,1),(69,2)]
A = [(64,1),(64,1),(64,1),(66,1),  (64,1),(66,1),(64,2),
     (64,1),(64,1),(69,1),(69,1),  (68,1),(66,1),(64,2),
     (64,1),(64,1),(64,1),(61,1),  (61,1),(65,1),(66,2),
     (66,1),(64,1),(64,1),(66,1),  (64,1),(69,1),(68,2),
     (64,1),(69,1),(69,1),(66,1),  (64,1),(62,1),(61,2)]
T = [(61,1),(59,1),(57,1),(57,1),  (57,1),(57,1),(57,1),(56,1),
     (57,1),(57,1),(61,1),(59,1),  (59,1),(57,1),(56,2),
     (61,1),(59,1),(57,1),(56,1),  (57,.5),(59,.5),(61,1),(61,2),
     (62,1),(59,1),(57,1),(57,1),  (57,1),(57,.5),(59,.5),(59,2),
     (57,1),(57,1),(57,1),(59,1),  (57,1),(56,1),(57,2)]
B = [(57,1),(56,1),(57,1),(50,1),  (49,1),(50,1),(52,2),
     (45,.5),(47,.5),(49,1),(54,1),(51,1),  (52,1),(47,1),(52,2),
     (57,1),(56,1),(57,1),(53,1),  (54,1),(49,1),(54,2),
     (54,1),(56,1),(57,1),(50,1),  (49,1),(50,.5),(51,.5),(52,2),
     (45,1),(50,1),(49,1),(50,1),  (52,1),(40,1),(45,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [("soprano", S, 82), ("alto", A, 66), ("tenor", T, 68), ("bass", B, 76)]
for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='A', time=0))
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(72), time=0))
        # gentle broadening in the last bar
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(62), time=9 * 4 * TPQ))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for n, d in notes:
        ticks = int(d * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=n, velocity=vel, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=n, velocity=0, time=ticks))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale/c13.mid')
