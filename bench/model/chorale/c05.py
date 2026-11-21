import mido

TPQ = 480
OUT = "/home/user/mxbench/model/chorale/c05.mid"

# (midi pitch, length in quarter notes); 8 bars of 4/4, D major
soprano = [(66,1),(69,1),(74,1),(73,1),  (71,.5),(69,.5),(67,.5),(66,.5),(64,2),
           (71,1),(73,1),(74,1),(76,1),  (73,1),(71,1),(69,2),
           (66,1),(66,1),(71,1),(73,1),  (74,1),(73,1),(71,2),
           (74,1),(76,1),(78,1),(76,1),  (74,1),(73,1),(74,2)]
alto    = [(62,1),(64,1),(62,1),(66,1),  (62,1),(64,1),(61,2),
           (66,1),(69,1),(69,1),(71,1),  (69,1),(69,.5),(68,.5),(64,2),
           (62,1),(61,1),(66,1),(66,1),  (66,1),(67,.5),(66,.5),(62,2),
           (67,2),(66,1),(67,1),         (66,1),(64,1),(62,2)]
tenor   = [(57,1),(57,1),(54,1),(57,1),  (59,1),(59,1),(57,2),
           (62,1),(64,1),(66,1),(64,1),  (64,1),(62,1),(61,2),
           (57,1),(58,1),(59,1),(64,1),  (62,1),(59,.5),(58,.5),(59,2),
           (59,1),(57,1),(57,1),(59,1),  (57,1),(55,1),(54,2)]
bass    = [(50,1),(49,1),(47,1),(54,1),  (55,.5),(54,.5),(52,1),(45,2),
           (47,1),(45,1),(42,1),(44,1),  (45,1),(52,1),(45,2),
           (50,1),(52,1),(50,1),(46,1),  (47,1),(52,.5),(54,.5),(47,2),
           (47,1),(49,1),(50,1),(55,1),  (57,1),(45,1),(50,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [("soprano", soprano, 84), ("alto", alto, 70), ("tenor", tenor, 72), ("bass", bass, 80)]

for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="D", time=0))
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(72), time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for pitch, q in notes:
        ticks = int(q * TPQ)
        tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=vel, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=ticks))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save(OUT)
