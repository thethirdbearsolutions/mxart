import mido

TPQ = 480
Q, H, E = 480, 960, 240

# Each voice: list of (midi pitch, duration in ticks), bar by bar. G minor, 4/4.
soprano = [
    (67, Q), (69, Q), (70, Q), (72, Q),
    (70, Q), (69, Q), (67, H),
    (70, Q), (72, Q), (74, Q), (75, Q),
    (74, Q), (72, Q), (70, H),
    (74, Q), (74, Q), (75, Q), (74, Q),
    (72, Q), (70, Q), (69, H),
    (74, Q), (72, Q), (70, Q), (67, Q),
    (69, Q), (66, Q), (67, H),
]
alto = [
    (62, Q), (62, Q), (62, Q), (60, Q),
    (62, Q), (62, E), (60, E), (58, H),
    (62, Q), (65, Q), (65, Q), (67, Q),
    (67, Q), (67, E), (69, E), (65, H),
    (65, Q), (65, Q), (63, Q), (67, Q),
    (67, Q), (67, Q), (66, H),
    (67, Q), (62, Q), (62, Q), (63, Q),
    (63, Q), (62, Q), (62, H),
]
tenor = [
    (58, Q), (57, Q), (55, Q), (55, Q),
    (55, Q), (54, Q), (55, H),
    (55, Q), (60, Q), (58, Q), (58, Q),
    (58, Q), (60, Q), (62, H),
    (58, Q), (55, Q), (55, Q), (62, Q),
    (63, Q), (64, Q), (57, H),
    (55, Q), (54, Q), (55, Q), (58, Q),
    (60, Q), (60, Q), (59, H),
]
bass = [
    (55, Q), (54, Q), (55, Q), (51, Q),
    (50, Q), (50, Q), (43, H),
    (43, Q), (45, Q), (46, Q), (51, Q),
    (55, Q), (51, E), (53, E), (46, H),
    (46, Q), (47, Q), (48, Q), (46, Q),
    (48, Q), (49, Q), (50, H),
    (46, Q), (45, Q), (43, Q), (51, Q),
    (48, Q), (50, Q), (43, H),
]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate(
        [("soprano", soprano), ("alto", alto), ("tenor", tenor), ("bass", bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(72), time=0))
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="Gm", time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    for pitch, dur in notes:
        tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=76, time=0))
        tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=dur))
    tr.append(mido.MetaMessage("end_of_track", time=0))

mid.save("/home/user/mxbench/model/chorale_hint/d10.mid")
