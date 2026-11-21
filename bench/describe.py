"""Plain descriptive numbers per tune, model against human: where do they differ at all?"""
import sys, statistics as st
from collections import Counter
sys.path.insert(0, "/home/user/mxart")
import mxart, bench

def stats(doc):
    out = []
    for t in doc.tracks:
        ns = sorted(t.notes, key=lambda n: n.start)
        if len(ns) < 8: continue
        ps = [n.pitch for n in ns]
        iv = [abs(b - a) for a, b in zip(ps, ps[1:])]
        g = doc.grid
        bars = [tuple((n.start % g, n.dur, n.pitch) for n in ns if b * g <= n.start < (b + 1) * g) for b in range(doc.nbars)]
        rhy = [tuple((x[0], x[1]) for x in b) for b in bars]
        out.append({
            "range (semitones)": max(ps) - min(ps),
            "most-used pitch share %": 100 * Counter(ps).most_common(1)[0][1] / len(ps),
            "steps (<=2 semitones) %": 100 * sum(i <= 2 for i in iv) / len(iv),
            "repeated notes %": 100 * sum(i == 0 for i in iv) / len(iv),
            "leaps >= a 5th %": 100 * sum(i >= 7 for i in iv) / len(iv),
            "distinct note lengths": len({n.dur for n in ns}),
            "bars with a new rhythm %": 100 * len(set(rhy)) / len(rhy),
            "bars with new notes %": 100 * len(set(bars)) / len(bars),
            "off-beat attacks %": 100 * sum(not doc.on_beat(n.start) for n in ns) / len(ns),
            "rests (share of time) %": 100 * (1 - sum(n.dur for n in ns) / (doc.nbars * g)),
            "last note is the tonic %": 100 * ((ns[-1].pitch - doc.key[0]) % 12 == 0),
        })
    return out

for fam in (("folk", "chorale") if __name__ == "__main__" else ()):
    h = [s for _, d, _ in bench.corpus("human", fam) for s in stats(d)]
    m = [s for _, d, _ in bench.corpus("model", fam) for s in stats(d)]
    if not m: print(f"\n{fam}: no model tunes yet"); continue
    print(f"\n{fam}: per voice, median (10th-90th percentile)   human n={len(h)}  model n={len(m)}")
    for k in h[0]:
        def f(xs):
            v = sorted(x[k] for x in xs); return f"{st.median(v):6.1f} ({v[len(v) // 10]:.0f}-{v[-1 - len(v) // 10]:.0f})"
        print(f"  {k:<28} human {f(h):<18} model {f(m)}")
