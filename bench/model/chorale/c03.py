import mido

TPQ = 480
Q = TPQ
E = TPQ // 2
H = 2 * Q
DH = 3 * Q

# (midi note, duration in ticks); 12 bars of 3/4 in G major
soprano = [
    (74, Q), (71, Q), (72, Q),          # 1
    (74, H), (76, Q),                   # 2
    (74, Q), (72, Q), (71, Q),          # 3
    (69, DH),                           # 4
    (71, Q), (72, Q), (74, Q),          # 5
    (76, H), (74, Q),                   # 6
    (76, Q), (74, Q), (73, Q),          # 7
    (74, DH),                           # 8
    (74, Q), (76, Q), (78, Q),          # 9
    (79, H), (76, Q),                   # 10
    (74, Q), (72, E), (71, E), (69, Q), # 11
    (67, DH),                           # 12
]
alto = [
    (67, Q), (67, Q), (64, Q),
    (67, H), (67, Q),
    (67, Q), (69, Q), (67, Q),
    (66, DH),
    (67, Q), (66, Q), (67, Q),
    (67, Q), (64, Q), (67, Q),
    (64, Q), (66, Q), (64, E), (67, E),
    (66, DH),
    (67, Q), (67, Q), (69, Q),
    (71, H), (67, Q),
    (67, Q), (69, Q), (66, Q),
    (67, DH),
]
tenor = [
    (59, Q), (59, Q), (57, Q),
    (55, Q), (59, Q), (60, Q),
    (62, Q), (64, Q), (62, Q),
    (62, H), (60, Q),
    (59, Q), (62, Q), (62, Q),
    (60, H), (62, Q),
    (59, Q), (57, Q), (57, Q),
    (57, DH),
    (62, Q), (59, Q), (62, Q),
    (62, H), (59, Q),
    (62, Q), (64, Q), (60, Q),
    (59, DH),
]
bass = [
    (55, Q), (52, Q), (48, Q),
    (47, Q), (43, Q), (48, Q),
    (47, Q), (48, Q), (50, Q),
    (50, DH),
    (43, Q), (45, Q), (47, Q),
    (48, Q), (45, Q), (47, Q),
    (43, Q), (45, H),
    (50, H), (48, Q),
    (47, Q), (52, Q), (50, Q),
    (55, Q), (54, Q), (52, Q),
    (47, Q), (48, Q), (50, Q),
    (43, DH),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate(
        [("soprano", soprano), ("alto", alto), ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(84), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=3, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="G", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for note, dur in notes:
        tr.append(mido.Message("note_on", channel=ch, note=note, velocity=76, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=note, velocity=0, time=dur))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save("/home/user/mxbench/model/chorale/c03.mid")
