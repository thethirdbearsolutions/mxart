import mido

TPQ = 480
OUT = "/home/user/mxbench/model/chorale/c08.mid"

# (midi pitch, length in quarter notes); 12 bars of 3/4, D minor
soprano = [(69,1),(69,1),(74,1), (73,1),(74,1),(76,1), (77,2),(74,1), (76,3),
           (72,2),(74,1), (76,1),(77,1),(74,.5),(72,.5), (70,1),(69,1),(67,1), (65,3),
           (69,1),(70,1),(72,1), (74,1),(79,1),(77,1), (76,1),(74,1),(73,1), (74,3)]
alto    = [(65,1),(65,1),(69,1), (69,1),(69,1),(69,1), (69,2),(67,1), (64,3),
           (65,2),(65,1), (67,1),(65,1),(65,1), (67,1),(65,1),(64,1), (60,3),
           (65,1),(67,1),(65,1), (69,1),(70,1),(69,1), (67,1),(65,1),(67,1), (67,1),(66,2)]
tenor   = [(62,1),(60,1),(65,1), (64,1),(62,1),(61,1), (62,3), (62,1),(61,2),
           (57,1),(60,1),(58,1), (58,1),(57,1),(58,1), (62,1),(60,1),(58,1), (58,1),(57,2),
           (57,1),(62,1),(60,1), (65,1),(61,1),(62,1), (58,1),(62,1),(64,1), (62,3)]
bass    = [(50,1),(53,.5),(52,.5),(50,1), (45,1),(53,1),(52,1), (50,1),(48,1),(46,1), (45,3),
           (53,1),(57,1),(50,1), (48,1),(53,1),(46,1), (43,1),(48,1),(48,1), (41,3),
           (50,1),(43,1),(45,1), (50,1),(52,1),(53,1), (55,1),(57,1),(45,1), (50,3)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate([("soprano", soprano, 84), ("alto", alto, 70),
                                         ("tenor", tenor, 70), ("bass", bass, 78)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(80), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=3, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Dm", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for pitch, ln in notes:
        tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=vel, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=int(ln * TPQ)))
    tr.append(mido.MetaMessage("end_of_track", time=0))
mid.save(OUT)
