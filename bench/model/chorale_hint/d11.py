import mido

TPQ = 480
OUT = "/home/user/mxbench/model/chorale_hint/d11.mid"

# (midi pitch, length in quarter notes); 8 bars of 4/4 in Eb major
soprano = [
    (67,1),(68,1),(70,1),(68,1),  (67,1),(65,1),(67,2),
    (70,1),(72,1),(74,1),(70,1),  (70,1),(69,1),(70,2),
    (68,1),(67,1),(67,1),(65,1),  (63,1),(62,1),(63,2),
    (70,1),(75,.5),(74,.5),(72,.5),(70,.5),(68,1),  (67,1),(65,1),(63,2),
]
alto = [
    (63,1),(62,1),(63,1),(65,1),  (63,1),(62,1),(63,2),
    (63,1),(63,1),(65,1),(60,1),  (62,1),(63,1),(62,2),
    (65,1),(63,.5),(62,.5),(60,1),(60,1),  (58,1),(58,1),(55,2),
    (63,1),(63,1),(63,1),(65,1),  (63,1),(62,1),(58,2),
]
tenor = [
    (58,1),(58,1),(58,1),(60,1),  (58,1),(58,1),(58,2),
    (55,1),(55,1),(58,1),(55,1),  (58,1),(60,1),(58,2),
    (58,1),(58,1),(58,1),(56,1),  (55,1),(53,1),(51,2),
    (55,1),(58,1),(60,1),(60,1),  (58,1),(56,1),(55,2),
]
bass = [
    (39,1),(41,1),(43,1),(44,1),  (46,1),(46,1),(39,2),
    (51,.5),(50,.5),(48,1),(46,1),(51,1),  (53,1),(53,1),(46,2),
    (50,1),(51,1),(52,1),(53,1),  (46,1),(46,1),(48,2),
    (51,1),(43,1),(44,1),(44,1),  (46,1),(46,1),(51,2),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate(
        [("soprano", soprano), ("alto", alto), ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Eb", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for pitch, beats in notes:
        tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=76, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=int(beats * TPQ)))
    tr.append(mido.MetaMessage("end_of_track", time=0))
mid.save(OUT)
