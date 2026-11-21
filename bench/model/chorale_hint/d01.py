import mido

TPQ = 480
OUT = "/home/user/mxbench/model/chorale_hint/d01.mid"

# (midi note, length in quarter notes); 8 bars of 4/4 in C major
soprano = [
    (72, 1), (71, 1), (72, 1), (74, 1),
    (76, 1), (74, 1), (72, 2),
    (76, 1), (74, 1), (72, 1), (71, 1),
    (69, 1), (69, 1), (67, 2),
    (67, 1), (72, 1), (71, 1), (69, 1),
    (74, 1), (72, .5), (71, .5), (69, 2),
    (77, 1), (76, 1), (72, 1), (74, 1),
    (72, 1), (71, 1), (72, 2),
]
alto = [
    (64, 1), (62, 1), (60, 1), (65, 1),
    (64, 1), (65, 1), (64, 2),
    (67, 1), (67, 1), (64, 1), (64, 1),
    (60, 1), (62, 1), (62, 2),
    (64, 1), (64, 1), (64, 1), (64, 1),
    (62, 1), (64, 1), (60, 2),
    (65, 1), (67, 1), (64, 1), (65, 1),
    (64, 1), (62, 1), (60, 2),
]
tenor = [
    (55, 1), (55, 1), (55, 1), (59, 1),
    (55, 1), (59, 1), (60, 2),
    (55, 1), (55, 1), (57, 1), (55, 1),
    (57, 1), (60, 1), (60, 1), (59, 1),
    (55, 1), (57, 1), (59, 1), (60, 1),
    (57, 1), (56, 1), (57, 2),
    (57, 1), (60, 1), (60, 1), (57, 1),
    (55, 1), (53, 1), (52, 2),
]
bass = [
    (48, 1), (43, 1), (52, 1), (50, 1),
    (48, 1), (43, 1), (48, 2),
    (48, 1), (47, 1), (45, 1), (52, 1),
    (53, 1), (54, 1), (55, 2),
    (48, 1), (45, 1), (44, 1), (45, 1),
    (53, 1), (52, 1), (45, 2),
    (50, 1), (52, 1), (57, .5), (55, .5), (53, 1),
    (55, 1), (43, 1), (48, 2),
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
        tr.append(mido.MetaMessage("key_signature", key="C", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for pitch, beats in notes:
        ticks = int(beats * TPQ)
        tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=76, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=ticks))
    tr.append(mido.MetaMessage("end_of_track", time=0))
mid.save(OUT)
