"""The textbook part-writing faults, counted the same way in Bach and in the model chorales."""
import sys
from itertools import combinations
sys.path.insert(0, "/home/user/mxart")
import bench

def faults(doc):
    vs = [t for t in doc.tracks if t.notes][:4]
    snd = []
    for t in vs:
        m = {}
        for n in t.notes:
            for k in range(n.dur): m[n.start + k] = n.pitch
        snd.append(m)
    par5 = par8 = cross = moves = 0
    cells = doc.nbars * doc.grid
    for a, b in combinations(range(len(vs)), 2):       # a is the higher voice
        for c in range(1, cells):
            p = (snd[a].get(c - 1), snd[b].get(c - 1), snd[a].get(c), snd[b].get(c))
            if None in p: continue
            if p[0] != p[2] and p[1] != p[3]:          # both voices moved
                moves += 1
                same_dir = (p[2] - p[0]) * (p[3] - p[1]) > 0
                i0, i1 = (p[0] - p[1]) % 12, (p[2] - p[3]) % 12
                if same_dir and i0 == i1 == 7: par5 += 1
                if same_dir and i0 == i1 == 0: par8 += 1
    for c in range(cells):
        col = [s.get(c) for s in snd]
        cross += any(x is not None and y is not None and x < y for x, y in zip(col, col[1:]))
    return par5, par8, cross, moves, cells

for src in (("human", "model") if __name__ == "__main__" else ()):
    items = bench.corpus(src, "chorale")
    tot = [0] * 5; tunes5 = tunes8 = 0
    for _, d, _ in items:
        f = faults(d); tot = [x + y for x, y in zip(tot, f)]
        tunes5 += f[0] > 0; tunes8 += f[1] > 0
    print(f"{src}: {len(items)} chorales; parallel 5ths {tot[0]} ({1000 * tot[0] / tot[3]:.1f} per 1000 paired moves, in {tunes5} pieces); "
          f"parallel octaves {tot[1]} ({1000 * tot[1] / tot[3]:.1f} per 1000, in {tunes8} pieces); "
          f"voices crossed {100 * tot[2] / tot[4]:.1f}% of the time")
