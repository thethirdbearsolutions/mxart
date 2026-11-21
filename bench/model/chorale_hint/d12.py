import mido

Q = 480
E = 240
H = 960
DH = 1440

# (pitch, duration) per voice, bar by bar; C minor, 4/4, 8 bars
soprano = [
    (67, Q), (72, Q), (74, Q), (75, Q),
    (74, Q), (72, Q), (71, H),
    (79, Q), (77, Q), (75, Q), (74, Q),
    (75, Q), (77, Q), (75, H),
    (67, Q), (68, Q), (70, Q), (72, Q),
    (75, Q), (74, DH),
    (75, Q), (77, Q), (79, Q), (77, Q),
    (75, Q), (74, Q), (72, H),
]
alto = [
    (63, Q), (67, Q), (65, Q), (63, Q),
    (65, Q), (63, E), (65, E), (67, H),
    (67, Q), (68, Q), (67, Q), (65, Q),
    (67, Q), (65, E), (68, E), (67, H),
    (63, Q), (62, Q), (63, Q), (60, Q),
    (67, Q), (67, DH),
    (67, Q), (68, Q), (67, Q), (68, Q),
    (67, Q), (67, E), (65, E), (63, H),
]
tenor = [
    (55, Q), (55, Q), (59, Q), (55, Q),
    (55, Q), (60, Q), (62, H),
    (63, Q), (58, Q), (58, Q), (58, Q),
    (58, Q), (60, E), (62, E), (58, H),
    (58, Q), (58, Q), (58, Q), (56, Q),
    (60, Q), (59, DH),
    (60, Q), (62, Q), (63, E), (62, E), (60, Q),
    (60, Q), (59, Q), (60, H),
]
bass = [
    (48, E), (50, E), (51, Q), (50, Q), (48, Q),
    (47, Q), (48, Q), (43, H),
    (48, Q), (50, Q), (51, Q), (56, Q),
    (55, Q), (56, E), (58, E), (51, H),
    (51, Q), (53, Q), (55, Q), (53, Q),
    (55, Q), (43, DH),
    (48, Q), (53, Q), (51, Q), (53, Q),
    (55, Q), (43, Q), (48, H),
]

mid = mido.MidiFile(type=1, ticks_per_beat=Q)
for ch, (name, notes) in enumerate(
        [("soprano", soprano), ("alto", alto), ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Cm", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for p, d in notes:
        tr.append(mido.Message("note_on", channel=ch, note=p, velocity=80, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=p, velocity=0, time=d))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save("/home/user/mxbench/model/chorale_hint/d12.mid")
