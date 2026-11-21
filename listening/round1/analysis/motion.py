"""For each repaired chorale: what did the repair do to motion, chord completeness and the bass, and which did the listener prefer?"""
import sys, json
sys.path.insert(0, "/home/user/mxart"); import mxart
R = "/home/user/mxrepair"; N = mxart.SHARP
PREF = {"c09": "repair (faint; not repeated)", "c01": "original", "c04": "original, certain", "c03": "original, certain", "c05": "original",
        "c07": "repair, certain", "a2": "original, certain (twice)", "c10": "original, certain", "c06": "no difference"}
def doc(stem, w):
    return mxart.parse(open(f"{R}/orig/{stem}.mx" if w == "orig" else f"{R}/A/{stem}/piece.mx").read(), stem)
def triad(pcs):
    """(root, quality, has_third, has_fifth) of the best-fitting major/minor triad, or None."""
    best = None
    for root in range(12):
        for q, third in (("", 4), ("m", 3)):
            tones = {root, (root + third) % 12, (root + 7) % 12}
            extra = len(pcs - tones - {(root + 10) % 12})        # allow a seventh
            if extra == 0 and root in pcs:
                score = len(pcs & tones)
                if best is None or score > best[0]: best = (score, root, q, (root + third) % 12 in pcs, (root + 7) % 12 in pcs)
    return best and best[1:]
def beats(d):
    cpb = d.grid // d.num; out = []
    snd = {}
    for t in d.tracks:
        for n in t.notes:
            for k in range(n.dur): snd.setdefault(n.start + k, {})[t.name] = n.pitch
    for b in range(d.nbars * d.num):
        v = snd.get(b * cpb, {})
        out.append((triad({p % 12 for p in v.values()}), v.get("bass")))
    return out
def offbeat(d): return sum(not d.on_beat(n.start) for t in d.tracks for n in t.notes)
print(f"{'':<5}{'off-beat attacks':>17}{'chords missing a third':>24}{'beats where the chord or its bass note changed':>48}   listener preferred")
rows = []
for stem in PREF:
    o, f = doc(stem, "orig"), doc(stem, "fixed"); bo, bf = beats(o), beats(f)
    m3o = sum(1 for c, _ in bo if c and not c[2]); m3f = sum(1 for c, _ in bf if c and not c[2])
    changes = []
    for i, ((co, bso), (cf, bsf)) in enumerate(zip(bo, bf)):
        if (co and co[:2]) != (cf and cf[:2]) or (bso is not None and bsf is not None and bso % 12 != bsf % 12):
            name = lambda c, b: (N[c[0]] + c[1] if c else "?") + ("/" + N[b % 12] if b is not None and c and b % 12 != c[0] else "")
            changes.append(f"bar {i // o.num + 1} beat {i % o.num + 1}: {name(co, bso)} -> {name(cf, bsf)}")
    do = offbeat(f) - offbeat(o)
    print(f"{stem:<5}{offbeat(o):>8} -> {offbeat(f):<5}{m3o:>12} -> {m3f:<8}{'; '.join(changes) or 'none':<50} {PREF[stem]}")
    rows.append((stem, do, m3f - m3o, len(changes)))
print()
for stem, dmot, dthird, nch in rows:
    score = dmot * 1 - dthird * 1 - nch * 1        # more motion good, fewer missing thirds good, changed harmony bad
    pred = "repair" if score > 0 else "original" if score < 0 else "no difference"
    print(f"{stem:<5} motion {dmot:+d}, missing thirds {dthird:+d}, harmony changes {nch}: predicts {pred:<14} heard: {PREF[stem]}")
