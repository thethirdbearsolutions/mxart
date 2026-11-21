import mido

TPQ = 480
S = [(69,1),(72,1),(74,1),(72,1), (69,1),(70,1),(67,2), (65,1),(67,1),(69,1),(69,.5),(70,.5),
     (72,1),(72,1),(71,1),(72,1), (72,1),(74,1),(72,1),(72,1), (77,1),(76,.5),(74,.5),(73,2),
     (74,1),(72,1),(70,1),(69,1), (67,1),(67,1),(65,2)]
A = [(65,1),(65,1),(65,1),(64,1), (62,1),(62,1),(64,2), (60,1),(60,1),(60,1),(62,1),
     (60,1),(62,1),(62,1),(64,1), (65,1),(65,1),(67,1),(65,1), (65,1),(67,1),(64,2),
     (65,1),(65,1),(65,1),(65,1), (65,1),(64,1),(60,2)]
T = [(60,1),(60,1),(58,1),(55,1), (53,1),(55,1),(55,2), (57,1),(58,1),(57,1),(53,1),
     (55,1),(57,1),(55,1),(55,1), (57,1),(58,1),(58,1),(57,1), (57,1),(55,1),(57,2),
     (57,1),(60,1),(62,1),(60,1), (62,1),(60,.5),(58,.5),(57,2)]
B = [(53,1),(45,1),(46,1),(48,1), (50,1),(46,1),(48,2), (53,1),(52,1),(53,1),(50,1),
     (52,1),(53,1),(43,1),(48,1), (53,.5),(52,.5),(50,1),(52,1),(53,1), (50,1),(46,1),(45,2),
     (50,1),(45,1),(46,1),(41,1), (46,1),(48,1),(41,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, notes) in enumerate([("soprano",S),("alto",A),("tenor",T),("bass",B)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(72), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='F', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for pitch, beats in notes:
        d = int(beats * TPQ)
        tr.append(mido.Message('note_on', channel=ch, note=pitch, velocity=76, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=pitch, velocity=0, time=d))
    tr.append(mido.MetaMessage('end_of_track', time=0))
mid.save('/home/user/mxbench/model/chorale_hint/d07.mid')
