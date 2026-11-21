import mido

# C major, 4/4, 16 bars
N = dict(C4=60, D4=62, E4=64, F4=65, Fs4=66, G4=67, Gs4=68, A4=69, Bb4=70, B4=71,
         C5=72, Cs5=73, D5=74, Eb5=75, E5=76, F5=77, Fs5=78, G5=79, A5=81, R=None)
TPQ = 480
melody = """
C4:1 E4:1 G4:1 G4:1 | A4:1 G4:.5 E4:.5 G4:2 |
F4:1 E4:.5 D4:.5 E4:1 C4:1 | D4:1 E4:.5 F4:.5 D4:2 |
C4:1 E4:1 G4:1 G4:1 | A4:1 C5:.5 A4:.5 G4:2 |
F4:1 A4:.5 G4:.5 E4:1 D4:1 | E4:1 D4:1 C4:2 |
C5:1.5 B4:.5 A4:1 G4:1 | A4:1 G4:.5 E4:.5 G4:2 |
C5:1.5 B4:.5 A4:1 G4:1 | A4:.5 G4:.5 F4:.5 E4:.5 D4:2 |
C4:1 E4:1 G4:1 G4:1 | A4:1 C5:.5 A4:.5 G4:2 |
F4:1 A4:.5 G4:.5 E4:1 D4:1 | E4:1 D4:1 C4:2
"""
mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
tr = mido.MidiTrack()
mid.tracks.append(tr)
tr.append(mido.MetaMessage('track_name', name='melody', time=0))
tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(104), time=0))
tr.append(mido.Message('program_change', channel=0, program=73, time=0))
rest = 0
for tok in melody.replace('|', ' ').split():
    name, beats = tok.split(':')
    ticks = int(round(float(beats) * TPQ))
    if N[name] is None:
        rest += ticks
        continue
    tr.append(mido.Message('note_on', channel=0, note=N[name], velocity=80, time=rest))
    tr.append(mido.Message('note_off', channel=0, note=N[name], velocity=0, time=ticks))
    rest = 0
tr.append(mido.MetaMessage('end_of_track', time=rest))
mid.save('/home/user/mxbench/model/folk/b1.mid')
