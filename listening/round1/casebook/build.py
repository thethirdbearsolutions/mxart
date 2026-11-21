import sys, html, json
from itertools import combinations
sys.path.insert(0, "/home/user/mxart"); import mxart
R = "/home/user/mxrepair"; V = ["soprano", "alto", "tenor", "bass"]
ORDER = ["c09", "c01", "c04", "c03", "c05", "c07", "a2", "c10", "c06"]
PAIRS = {"c09": "Pairs 1 and 11", "c01": "Pair 2", "c04": "Pair 3", "c03": "Pair 4", "c05": "Pairs 5 and 12", "c07": "Pair 6", "a2": "Pairs 7 and 10", "c10": "Pair 8", "c06": "Pair 9"}
AUDIO = {"c09": ("t01x", "t01y"), "c01": ("t02x", "t02y"), "c04": ("t03y", "t03x"), "c03": ("t04x", "t04y"), "c05": ("t05x", "t05y"),
         "c07": ("t06x", "t06y"), "a2": ("t07y", "t07x"), "c10": ("t08y", "t08x"), "c06": ("t09x", "t09y")}
VERDICT = {
 "c09": ("repair", "You preferred the repair, faintly, the first time. When the pair came back with the sides swapped you heard no difference."),
 "c01": ("original", "You preferred the original, fairly sure, and heard something wrong in the repair."),
 "c04": ("original", "You preferred the original, certain: it “has quite a few more notes in the counterpoint, which sounds very good and adds richness and complexity.”"),
 "c03": ("original", "You preferred the original, certain. Of the repair: in bar 1 the new note is “way too close to the primary line's note”, and bar 6 has the glitch sound."),
 "c05": ("original", "You preferred the original: the repair “sounds dissonant”, the original “sounds resolved.” Pair 12 was this original on both sides, and you heard no difference."),
 "c07": ("repair", "You preferred the repair, certain: the original “sounds too simplistic.”"),
 "a2": ("original", "You preferred the original both times. Of the repair: bars 1, 3 and 4 “don't sound wrong, they just sound boring.”"),
 "c10": ("original", "You preferred the original, certain: the repair “doesn't sound wrong at bar 7 so much as stomp stomp stomp.”"),
 "c06": ("none", "You heard no difference."),
}
def doc(stem, which):
    d = mxart.parse(open(f"{R}/orig/{stem}.mx" if which == "orig" else f"{R}/A/{stem}/piece.mx").read(), stem); assert not d.errors; return d
def parallels(d):
    snd = {t.name: {n.start + k: n for n in t.notes for k in range(n.dur)} for t in d.tracks}
    held = 2 * d.grid // d.num; out = []
    for a, b in combinations(V, 2):
        for c in range(1, d.nbars * d.grid):
            x0, y0, x1, y1 = snd[a].get(c - 1), snd[b].get(c - 1), snd[a].get(c), snd[b].get(c)
            if not (x0 and y0 and x1 and y1) or x0.pitch == x1.pitch or y0.pitch == y1.pitch: continue
            i0, i1 = (x0.pitch - y0.pitch) % 12, (x1.pitch - y1.pitch) % 12
            if i0 == i1 and i0 in (0, 7) and (x1.pitch - x0.pitch) * (y1.pitch - y0.pitch) > 0 and min(c - x0.start, c - y0.start) < held:
                out.append(dict(cell=c, a=a, b=b, n=(x0, y0, x1, y1), kind="5th" if i0 == 7 else "8ve"))
    return out
def keyset(d): return {(t.name, n.start, n.dur, n.pitch) for t in d.tracks for n in t.notes}
def roll(d, lo_cell, hi_cell, pmin, pmax, mark=None, changed=(), flats=False):
    CW, RH, GX, GY = 13, 9, 40, 20
    W = GX + (hi_cell - lo_cell) * CW + 6; H = GY + (pmax - pmin + 1) * RH + 8
    cpb = d.grid // d.num
    y = lambda p: GY + (pmax - p) * RH; x = lambda c: GX + (c - lo_cell) * CW
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" style="max-width:{W}px">']
    for p in range(pmin, pmax + 1):
        if p % 12 in (1, 3, 6, 8, 10): s.append(f'<rect class="blk" x="{GX}" y="{y(p)}" width="{W - GX - 6}" height="{RH}"/>')
        if p % 12 == 0 or p in (pmin, pmax): s.append(f'<text class="ax" x="{GX - 5}" y="{y(p) + RH - 1.5}" text-anchor="end">{mxart.name_of(p, flats)}</text>')
    for c in range(lo_cell, hi_cell + 1):
        if c % cpb == 0:
            bar = c % d.grid == 0
            s.append(f'<line class="{"barl" if bar else "beatl"}" x1="{x(c)}" y1="{GY - (10 if bar else 0)}" x2="{x(c)}" y2="{H - 8}"/>')
            if bar and c < hi_cell: s.append(f'<text class="ax" x="{x(c) + 4}" y="{GY - 5}">bar {c // d.grid + 1}</text>')
    involved = {mark["a"], mark["b"]} if mark else set()
    for t in d.tracks:
        for n in t.notes:
            a, b = max(n.start, lo_cell), min(n.start + n.dur, hi_cell)
            if a >= b: continue
            cls = f'n v-{t.name[0]}' + (" dim" if mark and t.name not in involved else "") + (" chg" if (t.name, n.start, n.dur, n.pitch) in changed else "")
            s.append(f'<rect class="{cls}" x="{x(a) + 1}" y="{y(n.pitch) + 1}" width="{(b - a) * CW - 2}" height="{RH - 2}" rx="2"/>')
    if mark:
        x0, y0, x1, y1 = mark["n"]
        for (up, dn, cell) in ((x0, y0, mark["cell"] - 1), (x1, y1, mark["cell"])):
            cx = x(cell) + CW / 2
            s.append(f'<line class="iv" x1="{cx}" y1="{y(up.pitch) + RH}" x2="{cx}" y2="{y(dn.pitch)}"/>')
            s.append(f'<text class="ivt" x="{cx + 4}" y="{(y(up.pitch) + RH + y(dn.pitch)) / 2 + 3}">{mark["kind"]}</text>')
    s.append("</svg>"); return "".join(s)
def nm(p, fl): return mxart.name_of(p, fl)
cases = []
for stem in ORDER:
    o, f = doc(stem, "orig"), doc(stem, "fixed"); fl = o.flats; g = o.grid; cpb = g // o.num
    ko, kf = keyset(o), keyset(f); added, removed = kf - ko, ko - kf
    ps = parallels(o); left = parallels(f)
    figs = []; seen = set()
    for p in ps:
        bar = p["cell"] // g
        if (bar, p["a"], p["b"]) in seen: continue
        seen.add((bar, p["a"], p["b"]))
        lo = max(0, (bar - (1 if p["cell"] % g < cpb * 2 else 0)) * g); hi = min(o.nbars * g, lo + 2 * g)
        pit = [n.pitch for d in (o, f) for t in d.tracks for n in t.notes if n.start < hi and n.start + n.dur > lo]
        pmin, pmax = min(pit) - 1, max(pit) + 1
        x0, y0, x1, y1 = p["n"]; step = x1.pitch - x0.pitch
        cap = (f'{p["a"].capitalize()} and {p["b"]}: {nm(x0.pitch, fl)} over {nm(y0.pitch, fl)}, then {nm(x1.pitch, fl)} over {nm(y1.pitch, fl)}. '
               f'Both move {"up" if step > 0 else "down"}, and both moments are {"a fifth" if p["kind"] == "5th" else "an octave"} apart.')
        ch = sorted(x for x in added if lo <= x[1] < hi); rm = sorted(x for x in removed if lo <= x[1] < hi)
        what = []
        for a_ in ch:
            same = [r for r in rm if r[0] == a_[0] and r[1] == a_[1]]
            if same and same[0][3] != a_[3]: what.append(f"{a_[0]} {nm(same[0][3], fl)} became {nm(a_[3], fl)} ({o.where(a_[1])})")
            elif same: what.append(f"{a_[0]} {nm(a_[3], fl)} is now held, and the passing note after it is gone ({o.where(a_[1])})")
        gone = [r for r in rm if not any(a_[0] == r[0] and a_[1] == r[1] for a_ in ch)]
        fixcap = "; ".join(what) if what else "No note in this window changed."
        figs.append(dict(bar=bar + 1, start=lo // g, cap=cap, fixcap=fixcap[0].upper() + fixcap[1:] + ("." if not fixcap.endswith(".") else ""),
                         orig=roll(o, lo, hi, pmin, pmax, mark=p, flats=fl), fixed=roll(f, lo, hi, pmin, pmax, changed=added, flats=fl)))
    cases.append(dict(stem=stem, key=f"{o.key[2]} {o.key[1]}", bars=o.nbars, beats=o.num, barSec=round(o.num * 60 / 76, 4), figs=figs,
                      n=len(ps), left=len(left), verdict=VERDICT[stem], pairs=PAIRS[stem], audio=AUDIO[stem]))
json.dump([{k: v for k, v in c.items() if k != "figs"} | {"nfig": len(c["figs"])} for c in cases], open("cases.json", "w"))
body = []
for i, c in enumerate(cases, 1):
    tag = {"original": "You preferred the original", "repair": "You preferred the repair", "none": "You heard no difference"}[c["verdict"][0]]
    body.append(f'<section class="case" id="{c["stem"]}"><header><h2>Chorale {i}, {html.escape(c["key"])}</h2><span class="meta">{c["pairs"]} on the listening bench · {c["bars"]} bars in {c["beats"]}/4 · {c["n"]} parallel{"s" if c["n"] != 1 else ""} flagged</span><span class="tag t-{c["verdict"][0]}">{tag}</span></header>')
    for j, fg in enumerate(c["figs"]):
        body.append(f'<div class="fig"><div class="col"><div class="lab"><b>As written</b><button class="play" type="button" id="p-{c["stem"]}-{j}-o" data-src="audio/{c["stem"]}-orig.mp3" data-at="{fg["start"] * c["barSec"]:.2f}" data-len="{2 * c["barSec"]:.2f}">Play these bars</button></div><div class="svgw">{fg["orig"]}</div><p class="cap">{html.escape(fg["cap"])}</p></div>'
                    f'<div class="col"><div class="lab"><b>Repaired</b><button class="play" type="button" id="p-{c["stem"]}-{j}-f" data-src="audio/{c["stem"]}-fixed.mp3" data-at="{fg["start"] * c["barSec"]:.2f}" data-len="{2 * c["barSec"]:.2f}">Play these bars</button></div><div class="svgw">{fg["fixed"]}</div><p class="cap">{html.escape(fg["fixcap"])}</p></div></div>')
    body.append(f'<p class="verdict">{html.escape(c["verdict"][1])}</p></section>')
open("cases.html", "w").write("\n".join(body))
print(sum(len(c["figs"]) for c in cases), "figures;", [(c["stem"], c["n"], c["left"], len(c["figs"])) for c in cases])
for c in cases:
    for fg in c["figs"]: print(c["stem"], "bar", fg["bar"], "|", fg["cap"], "|", fg["fixcap"])
