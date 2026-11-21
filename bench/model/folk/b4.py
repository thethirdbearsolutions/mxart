import mido

# A major, 2/4, 16 bars
N = dict(C4=60, D4=62, E4=64, F4=65, Fs4=66, G4=67, Gs4=68, A4=69, Bb4=70, B4=71,
         C5=72, Cs5=73, D5=74, Eb5=75, E5=76, F5=77, Fs5=78, G5=79, A5=81, R=None)
TPQ = 480
melody = """
A4:.5 Cs5:.5 E5:.5 E5:.5 | Fs5:.5 E5:.5 Cs5:1 | D5:.5 B4:.5 Cs5:.5 A4:.5 | B4:.5 Gs4:.5 E4:1 |
A4:.5 Cs5:.5 E5:.5 E5:.5 | Fs5:.5 A5:.5 E5:1 | D5:.5 Cs5:.25 B4:.25 A4:.5 Gs4:.5 | A4:1.5 R:.5 |
B4:.5 B4:.25 Cs5:.25 D5:.5 B4:.5 | Cs5:.5 Cs5:.25 D5:.25 E5:.5 Cs5:.5 | D5:.5 Fs5:.5 E5:.5 Cs5:.5 | B4:1 E4:1 |
A4:.5 Cs5:.5 E5:.5 E5:.5 | Fs5:.5 A5:.5 E5:1 | D5:.5 Cs5:.25 B4:.25 A4:.5 Gs4:.5 | A4:2
"""
mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
tr = mido.MidiTrack()
mid.tracks.append(tr)
tr.append(mido.MetaMessage('track_name', name='melody', time=0))
tr.append(mido.MetaMessage('time_signature', numerator=2, denominator=4, time=0))
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(108), time=0))
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
mid.save('/home/user/mxbench/model/folk/b4.mid')
