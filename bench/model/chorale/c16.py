import mido

TPQ = 480
# (midi pitch, length in quarter notes); nine bars of 4/4 in F minor
S = [(72,1),(72,1),(73,1),(72,1),  (68,1),(70,1),(67,2),
     (68,1),(72,1),(75,1),(73,1),  (72,1),(70,1),(68,2),
     (77,1),(75,1),(73,1),(72,1),  (68,1),(70,1),(72,2),
     (68,1),(70,1),(72,1),(73,1),  (72,1),(70,1),(68,1),(67,1),
     (65,4)]
A = [(68,1),(65,1),(65,1),(65,1),  (65,1),(65,2),(64,1),
     (65,1),(63,1),(67,.5),(65,.5),(63,1),  (63,1),(65,.5),(63,.5),(60,2),
     (65,1),(65,1),(65,1),(64,1),  (65,1),(65,1),(64,2),
     (65,1),(64,1),(65,1),(65,1),  (65,1),(64,1),(65,1),(61,.5),(60,.5),
     (60,1),(61,1),(60,2)]
T = [(60,1),(60,1),(58,1),(60,1),  (60,1),(61,1),(60,2),
     (60,1),(60,1),(58,1),(58,1),  (56,1),(56,.5),(55,.5),(56,2),
     (56,1),(57,1),(58,1),(58,1),  (56,.5),(55,.5),(53,1),(55,2),
     (56,1),(55,1),(56,1),(58,1),  (56,1),(55,1),(53,1),(53,.5),(52,.5),
     (53,1),(58,1),(57,2)]
B = [(53,1),(56,1),(58,1),(56,.5),(55,.5),  (53,1),(46,1),(48,2),
     (53,.5),(55,.5),(56,1),(51,1),(55,1),  (56,1),(49,.5),(51,.5),(44,2),
     (49,1),(48,1),(46,1),(48,1),  (53,1),(49,1),(48,2),
     (53,1),(55,1),(53,1),(46,1),  (48,1),(48,1),(49,1),(46,.5),(48,.5),
     (41,4)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate(
        [("soprano", S, 84), ("alto", A, 68), ("tenor", T, 70), ("bass", B, 76)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Fm", time=0))
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(66), time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message("note_on", channel=ch, note=p, velocity=vel, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=p, velocity=0, time=int(d * TPQ)))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save("/home/user/mxbench/model/chorale/c16.mid")
