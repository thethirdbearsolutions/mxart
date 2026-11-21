import mido

TPQ = 480
OUT = "/home/user/mxbench/model/chorale/c01.mid"

# Each voice: list of bars; each bar is a list of (midi pitch, length in quarter notes).
# A length written as a negative number marks a phrase-ending note (slightly shortened for breath).
soprano = [
    [(72, 1), (74, 1), (76, 1), (72, 1)],
    [(74, 1), (72, 1), (71, -2)],
    [(72, 1), (71, 1), (72, 1), (74, 1)],
    [(76, 1), (74, 1), (72, -2)],
    [(76, 1), (74, 1), (72, 1), (71, 1)],
    [(72, 1), (69, 1), (67, -2)],
    [(74, 1), (76, 1), (74, 1), (72, 1)],
    [(74, 1), (71, 1), (69, -2)],
    [(72, 1), (74, 1), (76, 1), (77, 1)],
    [(76, 2), (74, -2)],
    [(76, 1), (79, 1), (77, 1), (76, 1)],
    [(74, 2), (72, 2)],
]
alto = [
    [(64, 1), (67, 1), (67, 1), (69, 1)],
    [(69, 1), (69, 1), (67, -2)],
    [(67, 1), (65, 1), (64, 1), (62, 1)],
    [(67, 1), (65, 1), (64, -2)],
    [(67, 1), (67, 1), (66, 1), (67, 1)],
    [(67, 1), (66, 1), (62, -2)],
    [(67, 1), (67, 1), (68, 1), (69, 1)],
    [(65, 1), (64, 0.5), (62, 0.5), (60, -2)],
    [(65, 1), (62, 1), (67, 1), (65, 1)],
    [(67, 2), (67, -2)],
    [(67, 1), (67, 1), (69, 1), (67, 1)],
    [(69, 1), (67, 0.5), (65, 0.5), (64, 2)],
]
tenor = [
    [(55, 1), (55, 1), (60, 1), (64, 1)],
    [(62, 1), (62, 1), (62, -2)],
    [(60, 1), (62, 1), (55, 1), (57, 0.5), (59, 0.5)],
    [(60, 1), (59, 1), (60, -2)],
    [(60, 1), (62, 1), (57, 1), (62, 1)],
    [(64, 1), (62, 0.5), (60, 0.5), (59, -2)],
    [(59, 1), (60, 1), (59, 1), (60, 0.5), (59, 0.5)],
    [(57, 1), (56, 1), (57, -2)],
    [(57, 1), (55, 1), (60, 0.5), (59, 0.5), (57, 1)],
    [(60, 2), (59, -2)],
    [(60, 1), (60, 1), (57, 1), (60, 1)],
    [(60, 1), (59, 1), (60, 2)],
]
bass = [
    [(48, 1), (47, 1), (48, 0.5), (47, 0.5), (45, 1)],
    [(53, 1), (54, 1), (55, -2)],
    [(52, 1), (50, 1), (48, 1), (53, 1)],
    [(55, 1), (43, 1), (48, -2)],
    [(48, 1), (47, 1), (45, 1), (43, 1)],
    [(48, 1), (50, 1), (43, -2)],
    [(55, 1), (48, 1), (52, 1), (45, 1)],
    [(50, 1), (52, 1), (45, -2)],
    [(45, 1), (47, 1), (48, 1), (50, 1)],
    [(55, 2), (43, -2)],
    [(48, 1), (52, 1), (50, 1), (52, 1)],
    [(53, 1), (55, 1), (48, 2)],
]

voices = [("soprano", soprano, 84), ("alto", alto, 70), ("tenor", tenor, 72), ("bass", bass, 80)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)

for ch, (name, bars, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("track_name", name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage("key_signature", key="C", time=0))
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(69), time=0))
    tr.append(mido.Message("program_change", channel=ch, program=19, time=0))
    pending = 0  # rest ticks carried to the next event
    for bi, bar in enumerate(bars):
        if ch == 0 and bi == 11:
            # broaden into the final cadence
            tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(56), time=pending))
            pending = 0
        for pitch, q in bar:
            total = int(abs(q) * TPQ)
            sounding = total - 120 if q < 0 else total
            tr.append(mido.Message("note_on", channel=ch, note=pitch, velocity=vel, time=pending))
            tr.append(mido.Message("note_off", channel=ch, note=pitch, velocity=0, time=sounding))
            pending = total - sounding
    tr.append(mido.MetaMessage("end_of_track", time=pending))

mid.save(OUT)
