import mido
# G major, 4/4
NOTES = """
G4:1 G4:.5 A4:.5 B4:1 D5:1 | E5:1 D5:.5 B4:.5 D5:2 |
C5:1 B4:.5 A4:.5 B4:1 G4:1 | A4:1 B4:.5 G4:.5 A4:2 |
G4:1 G4:.5 A4:.5 B4:1 D5:1 | E5:1 D5:.5 B4:.5 D5:2 |
C5:1 B4:.5 A4:.5 G4:1 F#4:.5 A4:.5 | G4:3 R:1 |
D5:1 E5:.5 F#5:.5 G5:1 E5:1 | D5:1 B4:.5 C5:.5 D5:2 |
E5:1 D5:.5 C5:.5 B4:1 G4:1 | A4:1 F#4:1 D4:2 |
G4:1 G4:.5 A4:.5 B4:1 D5:1 | E5:1 G5:1 D5:2 |
E5:.5 D5:.5 C5:.5 B4:.5 A4:1 F#4:1 | G4:3 R:1
"""
NAMES = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def pitch(n):
    octv = int(n[-1]); name = n[:-1]
    p = NAMES[name[0]] + 12*(octv+1)
    if name.endswith('#'): p += 1
    if name.endswith('b'): p -= 1
    return p
mid = mido.MidiFile(type=1, ticks_per_beat=480)
tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('track_name', name='melody', time=0))
tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
tr.append(mido.MetaMessage('key_signature', key='G', time=0))
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(108), time=0))
tr.append(mido.Message('program_change', channel=0, program=73, time=0))
wait = 0
for tok in NOTES.replace('|', ' ').split():
    name, dur = tok.split(':')
    ticks = int(round(float(dur) * 480))
    if name == 'R':
        wait += ticks
        continue
    p = pitch(name)
    tr.append(mido.Message('note_on', channel=0, note=p, velocity=84, time=wait))
    tr.append(mido.Message('note_off', channel=0, note=p, velocity=0, time=ticks))
    wait = 0
tr.append(mido.MetaMessage('end_of_track', time=wait))
mid.save('/home/user/mxbench/model/folk/a1.mid')
