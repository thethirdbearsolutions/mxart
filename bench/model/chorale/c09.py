import mido

TPQ = 480
OUT = "/home/user/mxbench/model/chorale/c09.mid"

# (midi pitch, length in quarter notes); bars separated for readability
soprano = [
    (70,1),(70,1),(72,1),(74,1),
    (75,1),(74,1),(72,2),
    (74,1),(75,1),(74,1),(72,1),
    (70,1),(69,1),(67,2),
    (70,1),(72,1),(74,.5),(72,.5),(70,1),
    (69,1),(67,1),(65,2),
    (70,.5),(72,.5),(74,.5),(75,.5),(77,1),(75,1),
    (74,1),(72,1),(70,2),
]
alto = [
    (65,1),(67,1),(65,1),(65,1),
    (63,1),(65,1),(65,2),
    (65,1),(63,1),(65,1),(65,1),
    (62,.5),(64,.5),(66,1),(62,2),
    (65,1),(63,1),(62,1),(62,1),
    (65,1),(64,1),(60,2),
    (65,1),(67,1),(68,1),(67,1),
    (65,1),(65,.5),(63,.5),(62,2),
]
tenor = [
    (62,1),(62,1),(60,1),(58,1),
    (58,1),(58,1),(58,1),(57,1),
    (58,1),(55,1),(58,1),(57,1),
    (58,1),(60,1),(58,2),
    (58,1),(57,1),(53,1),(55,1),
    (57,1),(58,1),(57,2),
    (62,1),(62,1),(58,1),(58,1),
    (58,1),(57,1),(58,2),
]
bass = [
    (58,.5),(57,.5),(55,1),(57,1),(58,1),
    (55,1),(50,.5),(51,.5),(53,2),
    (46,1),(48,1),(50,1),(53,1),
    (55,1),(50,1),(43,2),
    (50,1),(48,1),(46,.5),(45,.5),(43,1),
    (48,1),(48,1),(53,2),
    (46,.5),(45,.5),(43,1),(50,1),(51,1),
    (53,1),(41,1),(46,2),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes, vel) in enumerate([
        ("soprano", soprano, 84), ("alto", alto, 70),
        ("tenor", tenor, 70), ("bass", bass, 76)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Bb", time=0))
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(72), time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for pitch, beats in notes:
        ticks = int(beats * TPQ)
        tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=vel, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=ticks))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save(OUT)
