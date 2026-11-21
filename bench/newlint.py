import sys, copy, random
from collections import Counter
sys.path.insert(0, "/home/user/mxart")
import mxart, bench

def voiced(items):
    for _, d, _ in items:
        base = [t.name for t in d.tracks if "." not in t.name and t.notes]
        d.voices = [(1, base)] if len(base) >= 2 else []
    return items

def moves(doc):
    n = 0
    for _, names in doc.voices:
        vs = [next(t for t in doc.tracks if t.name == x) for x in names]
        snd = [{n_.start + k: n_.pitch for n_ in t.notes for k in range(n_.dur)} for t in vs]
        for a in range(len(vs)):
            for b in range(a + 1, len(vs)):
                for c in range(1, doc.nbars * doc.grid):
                    p = (snd[a].get(c - 1), snd[b].get(c - 1), snd[a].get(c), snd[b].get(c))
                    n += None not in p and p[0] != p[2] and p[1] != p[3]
    return n

print(f"{'':<24}{'pieces':>7} | per 1000 paired moves, mid-phrase / after a held note: {'5ths':>12}{'octaves':>14} | crossings per 100 bars | pieces with a mid-phrase 5th")
for src, fam, label in [("human", "chorale", "Bach chorales"), ("human", "corelli", "Corelli trio sonatas"), ("model", "chorale", "MODEL chorales")]:
    items = voiced(bench.corpus(src, fam))
    c, mv, bars, with5 = Counter(), 0, 0, 0
    for _, d, _ in items:
        w = mxart.lint(d, None)[1]
        k = Counter((x.split()[0], "held" in x) for x in w)
        c.update(k); mv += moves(d); bars += d.nbars; with5 += k[("W_PARALLEL_5TH", False)] > 0
    f = lambda code: f"{1000 * c[(code, False)] / mv:5.1f} /{1000 * c[(code, True)] / mv:5.1f}"
    print(f"{label:<24}{len(items):>7} | {'':<54}{f('W_PARALLEL_5TH'):>12}{f('W_PARALLEL_8VE'):>14} | {100 * c[('W_CROSSING', False)] / bars:>22.1f} | {with5} of {len(items)}")

items = voiced(bench.corpus("human", "chorale"))
rng = random.Random(11)
def inj_par(doc, rng):   # move one voice so it shadows another a fifth away for two attacks
    names = doc.voices[0][1]; a, b = rng.sample(range(len(names)), 2)
    A = next(t for t in doc.tracks if t.name == names[a]); B = next(t for t in doc.tracks if t.name == names[b])
    starts = {n.start: n for n in B.notes}
    pairs = [(x, y) for x, y in zip(A.notes, A.notes[1:]) if x.pitch != y.pitch and x.start in starts and y.start in starts and y.start == x.start + x.dur]
    if not pairs: return None
    x, y = rng.choice(pairs); off = 7 if a > b else -7
    starts[x.start].pitch = x.pitch + off; starts[y.start].pitch = y.pitch + off
    return x.start
bench.INJ["one voice shadows another a 5th away"] = inj_par
print("\ninjection into Bach, new default lint (caught = a warning the clean chorale didn't have)")
for name, fn in bench.INJ.items():
    tried = caught = 0; by = Counter()
    for _, doc, _ in items:
        base = Counter(mxart.lint(doc, None)[1])
        for _ in range(5):
            d = copy.deepcopy(doc)
            if fn(d, rng) is None: continue
            tried += 1; new = Counter(mxart.lint(d, None)[1]) - base
            if new: caught += 1; by.update({w.split()[0] for w in new})
    print(f"  {name:<38} {caught:>3} of {tried:>3} ({100 * caught / max(1, tried):3.0f}%)  by {dict(by.most_common(3))}")
