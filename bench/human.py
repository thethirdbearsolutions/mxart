"""Build the human corpus as MIDI: Bach chorales and Essen folk songs, from music21's bundled corpus."""
import json, os, random, sys
import mido
from music21 import corpus, converter, meter, stream

random.seed(7)
OUT = os.path.dirname(os.path.abspath(__file__)) + "/human"
meta = {}

def to_midi(score, path, names):
    parts = list(score.parts) if score.parts else [score]
    ts = score.recurse().getElementsByClass(meter.TimeSignature)
    sigs = {(t.numerator, t.denominator) for t in ts}
    if len(sigs) != 1:
        return "mixed metre"
    num, den = sigs.pop()
    if (num, den) not in ((4, 4), (3, 4), (2, 4)):
        return f"metre {num}/{den}"
    m0 = parts[0].getElementsByClass(stream.Measure)
    pad = float(m0[0].paddingLeft) if m0 else 0.0
    mf = mido.MidiFile(type=1, ticks_per_beat=480)
    t0 = mido.MidiTrack(); mf.tracks.append(t0)
    t0.append(mido.MetaMessage("time_signature", numerator=num, denominator=den, time=0))
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(100), time=0))
    total = 0
    for i, part in enumerate(parts):
        ev = []
        for n in part.stripTies().flatten().notes:
            if n.duration.quarterLength <= 0:
                continue
            s = round((float(n.offset) + pad) * 480); e = s + round(float(n.duration.quarterLength) * 480)
            for p in n.pitches:
                ev += [(s, 1, "note_on", p.midi), (e, 0, "note_off", p.midi)]
                total += 1
        tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr.append(mido.MetaMessage("track_name", name=names[i] if i < len(names) else f"p{i}", time=0))
        last = 0
        for tick, _, kind, p in sorted(ev):
            tr.append(mido.Message(kind, note=p, velocity=80 if kind == "note_on" else 0, channel=i, time=tick - last)); last = tick
    if total < 20:
        return "too short"
    k = score.analyze("key")
    mf.save(path)
    meta[os.path.relpath(path, OUT)] = {"key": k.tonic.name.replace("-", "b"), "mode": k.mode, "num": num, "den": den,
                                        "pickup": pad, "notes": total}
    return None

os.makedirs(OUT + "/chorale", exist_ok=True); os.makedirs(OUT + "/folk", exist_ok=True)
skipped = {}
files = sorted(str(p) for p in corpus.getComposer("bach") if "bwv" in os.path.basename(str(p)))
random.shuffle(files)
got = 0
for f in files:
    if got == 40: break
    try:
        sc = converter.parse(f)
        if len(sc.parts) != 4: skipped["not 4 parts"] = skipped.get("not 4 parts", 0) + 1; continue
        why = to_midi(sc, f"{OUT}/chorale/{os.path.basename(f).split('.')[0]}.mid", ["soprano", "alto", "tenor", "bass"])
    except Exception as e:
        why = "error " + type(e).__name__
    if why: skipped[why] = skipped.get(why, 0) + 1
    else: got += 1
print("chorales", got, "skipped", skipped)

skipped = {}; got = 0
ess = sorted(str(p) for p in corpus.getComposer("essenFolksong"))
random.shuffle(ess)
for f in ess[:8]:
    try:
        op = converter.parse(f)
    except Exception as e:
        skipped["opus error"] = skipped.get("opus error", 0) + 1; continue
    scores = list(op.scores)
    random.shuffle(scores)
    for j, sc in enumerate(scores[:8]):
        if got == 40: break
        try:
            why = to_midi(sc, f"{OUT}/folk/{os.path.basename(f).split('.')[0]}_{j}.mid", ["melody"])
        except Exception as e:
            why = "error " + type(e).__name__
        if why: skipped[why] = skipped.get(why, 0) + 1
        else: got += 1
print("folk", got, "skipped", skipped)
json.dump(meta, open(OUT + "/meta.json", "w"), indent=1)
