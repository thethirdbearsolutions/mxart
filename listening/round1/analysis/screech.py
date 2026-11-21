"""Is the 'signal screech' beating between partials of the synth? Predict it from the notes, then measure it in the audio."""
import sys, json, wave
import numpy as np
sys.path.insert(0, "/home/user/mxart"); import mxart
R = "/home/user/mxrepair"
KEY = json.load(open("/home/user/listen2/KEY_private.json"))
HARM = {False: [(1, 1.0), (3, .33), (5, .2), (7, .1)], True: [(1, 1.0), (2, .35), (3, .12)]}
def doc(stem, which):
    d = mxart.parse(open(f"{R}/orig/{stem}.mx" if which == "orig" else f"{R}/A/{stem}/piece.mx").read(), stem)
    d.tempo = 76
    for t in d.tracks: t.program, t.vel = 19, 90
    return d
def partials(p):
    f = 440 * 2 ** ((p - 69) / 12); bass = p < 48
    return [(f * h, a * (0.5 if bass else 0.28)) for h, a in HARM[bass]]
def predicted(d):
    """per beat: sum over pairs of partials from different notes that beat at 3-35 Hz, weighted by the weaker amplitude."""
    cpb = d.grid // d.num; out = []
    snd = {}
    for t in d.tracks:
        for n in t.notes:
            for k in range(n.dur): snd.setdefault(n.start + k, []).append((t.name, n.pitch))
    for b in range(d.nbars * d.num):
        notes = sorted(set(snd.get(b * cpb, [])))
        s = 0; worst = None
        for i in range(len(notes)):
            for j in range(i + 1, len(notes)):
                for f1, a1 in partials(notes[i][1]):
                    for f2, a2 in partials(notes[j][1]):
                        df = abs(f1 - f2)
                        if 3 <= df <= 35:
                            w = min(a1, a2); s += w
                            if worst is None or w > worst[0]: worst = (w, df, notes[i], notes[j])
        out.append((s, worst))
    return out
def measured(d):
    """per beat: how much the loudness wobbles at 3-35 Hz, from the rendered audio (no echo)."""
    mxart.to_wav(d, "/tmp/claude-0/-home-user/90fceaca-49e7-59cb-8abe-558dacb3fcd7/scratchpad/s.wav")
    w = wave.open("/tmp/claude-0/-home-user/90fceaca-49e7-59cb-8abe-558dacb3fcd7/scratchpad/s.wav"); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float) / 32768
    beat = int(sr * 60 / 76); out = []
    for b in range(d.nbars * d.num):
        seg = x[b * beat + int(0.08 * sr):(b + 1) * beat - int(0.02 * sr)]     # skip the attack
        env = np.abs(seg); k = int(sr / 60); env = np.convolve(env, np.ones(k) / k, "same")[::k]   # ~60 Hz envelope
        env = env - env.mean(); sp = np.abs(np.fft.rfft(env * np.hanning(len(env)))); fr = np.fft.rfftfreq(len(env), 1 / 60)
        band = sp[(fr >= 3) & (fr <= 28)].sum() / (np.abs(seg).mean() * len(env) + 1e-9)
        out.append(band)
    return out
if __name__ == "__main__":
    reported = {("c03", "fixed"): [6], ("a2", "fixed"): [7], ("c06", "orig"): [3], ("c06", "fixed"): [3]}
    for stem in ("c03", "a2", "c06", "c09", "c10", "c04"):
        for which in ("orig", "fixed"):
            d = doc(stem, which); pr = predicted(d); me = measured(d)
            bars = []
            for bar in range(d.nbars):
                p = max(pr[bar * d.num + k][0] for k in range(d.num)); m = max(me[bar * d.num + k] for k in range(d.num)); bars.append((p, m))
            pm = np.array(bars); rank_p = (-pm[:, 0]).argsort().argsort() + 1; rank_m = (-pm[:, 1]).argsort().argsort() + 1
            r = np.corrcoef([x[0] for x in pr], me)[0, 1]
            tag = reported.get((stem, which), [])
            print(f"{stem:<4}{which:<6} predicted-vs-measured r={r:.2f}  per bar measured wobble: " + " ".join(f"{'[' if b + 1 in tag else ''}{m * 100:.0f}{']' if b + 1 in tag else ''}" for b, (p, m) in enumerate(bars))
                  + (f"   reported bar {tag[0]} ranks {rank_m[tag[0] - 1]} of {d.nbars} measured, {rank_p[tag[0] - 1]} predicted" if tag else ""))
    # the worst moments in the reported bars
    for stem, which, bar in (("c03", "fixed", 6), ("c03", "orig", 6), ("a2", "fixed", 7), ("a2", "orig", 7), ("c06", "orig", 3)):
        d = doc(stem, which); pr = predicted(d)
        for k in range(d.num):
            s, w = pr[(bar - 1) * d.num + k]
            if w: print(f"   {stem} {which} bar {bar} beat {k + 1}: score {s:.2f}; strongest: {w[2][0]} {mxart.name_of(w[2][1])} with {w[3][0]} {mxart.name_of(w[3][1])}, partials {w[1]:.1f} Hz apart")
