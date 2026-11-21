import mido

TPQ = 480
# (midi pitch, length in quarter notes); 8 bars of 4/4 in F# minor
S = [(73,1),(73,1),(74,1),(73,1), (71,1),(69,1),(68,2),
     (69,1),(71,1),(73,1),(74,1), (73,1),(71,1),(69,2),
     (76,1),(74,1),(73,1),(71,1), (69,1),(71,1),(73,2),
     (78,1),(76,1),(74,1),(71,1), (69,1),(68,1),(66,2)]
A = [(69,1),(66,1),(66,1),(65,1), (61,1),(61,1),(65,2),
     (66,1),(64,1),(64,1),(66,1), (64,1.5),(62,.5),(61,2),
     (69,1),(66,1),(66,1),(65,1), (66,1),(66,1),(65,2),
     (66,1),(69,1),(66,1),(66,.5),(68,.5), (66,1),(65,1),(61,2)]
T = [(61,1),(57,1),(56,1),(56,1), (56,1),(57,.5),(59,.5),(61,2),
     (61,1),(59,1),(57,1),(57,1), (57,1),(56,1),(57,2),
     (61,1),(59,1),(57,1),(61,1), (61,1),(59,1),(56,2),
     (61,1),(57,1),(59,1),(59,1), (61,1),(61,.5),(59,.5),(58,2)]
B = [(54,1),(45,1),(47,1),(49,1), (53,1),(54,1),(49,2),
     (54,1),(56,1),(57,1),(50,1), (52,1),(52,1),(45,2),
     (57,1),(50,.5),(52,.5),(54,1),(56,1), (54,.5),(52,.5),(50,1),(49,2),
     (45,1),(49,1),(47,1),(50,1), (49,1),(49,1),(42,2)]

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
voices = [("soprano", S, 82), ("alto", A, 68), ("tenor", T, 70), ("bass", B, 76)]
for ch, (name, notes, vel) in enumerate(voices):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='F#m', time=0))
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(66), time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    rest = 0
    total = sum(d for _, d in notes)
    pos = 0
    for p, d in notes:
        ticks = int(d * TPQ)
        pos += d
        # breathe after cadence half notes, except the final chord
        gap = 120 if (d == 2 and pos < total) else 0
        tr.append(mido.Message('note_on', channel=ch, note=p, velocity=vel, time=rest))
        tr.append(mido.Message('note_off', channel=ch, note=p, velocity=0, time=ticks - gap))
        rest = gap
    tr.append(mido.MetaMessage('end_of_track', time=rest))

# slow the final cadence a little
t0 = mid.tracks[0]
t0.insert(4, mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(56), time=0))
# place it at start of bar 8 by moving it into a dedicated position: simpler to rebuild times
t0.pop(4)
abs_t = 0
for i, m in enumerate(t0):
    abs_t += m.time
    if abs_t >= 28 * TPQ and m.type == 'note_on':
        t0.insert(i, mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(56), time=m.time))
        m.time = 0
        break

mid.save('/home/user/mxbench/model/chorale/c14.mid')
