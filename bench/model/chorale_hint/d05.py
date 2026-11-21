import mido

TPQ = 480
N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def p(name):
    letter, rest = name[0], name[1:]
    acc = 0
    if rest[0] == '#':
        acc, rest = 1, rest[1:]
    return 12 * (int(rest) + 1) + N[letter] + acc

# (note, length in quarter notes); 8 bars of 4/4 in D major
soprano = "F#4 G4 A4 B4 | A4 G4 F#4:2 | A4 B4 C#5 D5 | E5 D5 C#5:2 | F#5 E5 D5 C#5 | D5 C#5 B4:2 | G4 B4 A4 G4 | F#4 E4 D4:2"
alto    = "D4 E4 D4 B3 | D4 C#4 D4:2 | D4 D4 E4 A4 | A4 G#4 E4:2 | D4 E4 F#4 E4 | D4 E4 D4:2 | D4 D4 F#4 E4 | D4 C#4 A3:2"
tenor   = "A3 B3 A3 G3 | F#3 E3 F#3:2 | F#3 F#3 A3 A3 | C#4 B3 A3:2 | A3 A3 A3 G3 | B3 A#3 B3:2 | B3 G3 A3 B3 | A3 A3:.5 G3:.5 F#3:2"
bass    = "D3 G3 F#3 E3 | A2 A2 D3:2 | D3 B2 A2 F#3 | E3 E3 A2:2 | D3 C#3 D3 E3 | F#3 F#3 B2:2 | G3 B2:.5 C#3:.5 D3 G2 | A2 A2 D3:2"

mid = mido.MidiFile(type=1, ticks_per_beat=TPQ)
for ch, (name, line) in enumerate([('soprano', soprano), ('alto', alto), ('tenor', tenor), ('bass', bass)]):
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch == 0:
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(76), time=0))
        tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        tr.append(mido.MetaMessage('key_signature', key='D', time=0))
    tr.append(mido.Message('program_change', channel=ch, program=19, time=0))
    for tok in line.replace('|', ' ').split():
        nm, _, d = tok.partition(':')
        ticks = int(round(float(d or 1) * TPQ))
        tr.append(mido.Message('note_on', channel=ch, note=p(nm), velocity=80, time=0))
        tr.append(mido.Message('note_off', channel=ch, note=p(nm), velocity=0, time=ticks))
    tr.append(mido.MetaMessage('end_of_track', time=0))

mid.save('/home/user/mxbench/model/chorale_hint/d05.mid')
