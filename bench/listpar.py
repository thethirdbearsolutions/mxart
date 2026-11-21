import sys
from itertools import combinations
sys.path.insert(0, "/home/user/mxart")
import mxart, bench
def cases(doc, want=7):
    vs = [t for t in doc.tracks if "." not in t.name and t.notes]
    snd, att = [], []
    for t in vs:
        m, a = {}, set()
        for n in t.notes:
            a.add(n.start)
            for k in range(n.dur): m[n.start + k] = n.pitch
        snd.append(m); att.append(a)
    out = []
    for a, b in combinations(range(len(vs)), 2):
        for c in range(1, doc.nbars * doc.grid):
            p = (snd[a].get(c - 1), snd[b].get(c - 1), snd[a].get(c), snd[b].get(c))
            if None in p or p[0] == p[2] or p[1] == p[3]: continue
            if (p[2] - p[0]) * (p[3] - p[1]) > 0 and (p[0] - p[1]) % 12 == (p[2] - p[3]) % 12 == want:
                # how long was each interval sounding? short = passing
                d0 = min(next(n.dur for n in vs[i].notes if n.start <= c - 1 < n.start + n.dur) for i in (a, b))
                d1 = min(next(n.dur for n in vs[i].notes if n.start == c) if c in att[i] else 0 for i in (a, b))
                out.append(f"{doc.where(c):<16} {vs[a].name}/{vs[b].name}: {mxart.name_of(p[0])}-{mxart.name_of(p[1])} -> "
                           f"{mxart.name_of(p[2])}-{mxart.name_of(p[3])}  (shorter note before: {d0} cells, after: {d1})")
    return out
for src in sys.argv[1:]:
    for stem, doc, _ in bench.corpus(src, "chorale"):
        cs = cases(doc)
        if cs: print(f"{src} {stem} ({doc.num}/{doc.den})"); print("   " + "\n   ".join(cs))
