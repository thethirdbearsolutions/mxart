import mido

TPQ = 480
Q = TPQ
E = TPQ // 2
H = TPQ * 2

# (midi note, duration in ticks) per voice; 8 bars of 4/4 in G minor
soprano = [
    (67, Q), (69, Q), (70, Q), (72, Q),      # 1
    (70, Q), (69, Q), (67, H),               # 2
    (70, Q), (72, Q), (74, Q), (75, Q),      # 3
    (74, Q), (72, Q), (70, H),               # 4
    (74, Q), (75, Q), (77, Q), (75, Q),      # 5
    (74, Q), (72, Q), (74, H),               # 6
    (74, Q), (72, Q), (70, Q), (72, Q),      # 7
    (70, Q), (69, Q), (67, H),               # 8
]
alto = [
    (62, Q), (62, Q), (62, Q), (63, Q),
    (62, Q), (62, E), (60, E), (58, H),
    (67, Q), (65, Q), (65, Q), (67, Q),
    (65, Q), (65, E), (63, E), (62, H),
    (67, Q), (67, Q), (65, Q), (66, Q),
    (67, Q), (67, Q), (67, Q), (66, Q),
    (67, Q), (69, Q), (67, Q), (68, Q),
    (67, Q), (66, Q), (62, H),
]
tenor = [
    (58, Q), (57, Q), (55, Q), (55, Q),
    (55, Q), (54, Q), (55, H),
    (62, Q), (60, Q), (58, Q), (58, Q),
    (58, Q), (57, Q), (58, H),
    (58, Q), (58, Q), (58, Q), (57, Q),
    (58, Q), (60, Q), (57, H),
    (58, E), (60, E), (62, Q), (62, Q), (63, Q),
    (62, Q), (62, E), (60, E), (59, H),
]
bass = [
    (55, Q), (54, Q), (55, Q), (48, Q),
    (50, Q), (50, Q), (43, H),
    (43, Q), (45, Q), (46, Q), (51, Q),
    (53, Q), (53, Q), (46, H),
    (55, E), (53, E), (51, Q), (50, Q), (48, Q),
    (46, Q), (51, Q), (50, H),
    (55, Q), (54, Q), (55, Q), (48, Q),
    (50, Q), (50, Q), (43, H),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [("soprano", soprano, 84), ("alto", alto, 70), ("tenor", tenor, 72), ("bass", bass, 78)]
for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(69), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Gm", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for n, d in notes:
        tr.append(mido.Message("note_on", channel=ch, note=n, velocity=vel, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=n, velocity=0, time=d))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save("/home/user/mxbench/model/chorale/c10.mid")
