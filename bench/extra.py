"""More human music: cut each piece into stretches of one time signature and write each as MIDI + key."""
import glob, json, os, sys
from fractions import Fraction as F
import mido
sys.path.insert(0, "/home/user/mxart")
import mxart

OUT = os.path.dirname(os.path.abspath(__file__)) + "/human"
MAJ = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MIN = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

def key_of(notes):
    h = [0.0] * 12
    for s, d, p in notes: h[p % 12] += float(d)
    def corr(a, b):
        ma, mb = sum(a) / 12, sum(b) / 12
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return num / den if den else 0
    best = max(((corr(h, [prof[(i - t) % 12] for i in range(12)]), t, mode)
                for t in range(12) for prof, mode in ((MAJ, "major"), (MIN, "minor"))))
    return NAMES[best[1]], best[2]

def write(family, stem, parts, sigs, meta, stats):
    """parts: [[(start, dur, pitch)]] in quarter notes; sigs: [(start, num, den)]."""
    end = max((s + d for p in parts for s, d, _ in p), default=0)
    sigs = sorted(set(sigs)) or [(0, 4, 4)]
    cuts = []
    for (s, n, d), nxt in zip(sigs, sigs[1:] + [(end, 0, 0)]):
        if cuts and cuts[-1][2:] == (n, d): cuts[-1] = (cuts[-1][0], nxt[0], n, d)
        else: cuts.append((s, nxt[0], n, d))
    stats["pieces"] += 1; stats["sig_changes"] += len(cuts) > 1
    os.makedirs(f"{OUT}/{family}", exist_ok=True)
    for k, (a, b, num, den) in enumerate(cuts):
        seg = [[(s - a, d, p) for s, d, p in part if a <= s < b] for part in parts]
        flat = [x for part in seg for x in part]
        if len(flat) < 60: continue
        if (F(16 * num, den)).denominator != 1: stats["odd_metre"] += 1; continue
        mf = mido.MidiFile(type=1, ticks_per_beat=480)
        t0 = mido.MidiTrack(); mf.tracks.append(t0)
        t0.append(mido.MetaMessage("time_signature", numerator=num, denominator=den, time=0))
        for i, part in enumerate(seg):
            ev = []
            for s, d, p in part:
                s2, e2 = round(s * 480), round((s + d) * 480)
                if e2 > s2: ev += [(s2, 1, "note_on", p), (e2, 0, "note_off", p)]
            tr = mido.MidiTrack(); mf.tracks.append(tr)
            tr.append(mido.MetaMessage("track_name", name=f"p{i}", time=0))
            last = 0
            for tick, _, kind, p in sorted(ev):
                tr.append(mido.Message(kind, note=p, velocity=80 if kind == "note_on" else 0, channel=i % 9, time=tick - last)); last = tick
        name = f"{stem}_{k}"
        mf.save(f"{OUT}/{family}/{name}.mid")
        tonic, mode = key_of(flat)
        meta[f"{family}/{name}.mid"] = {"key": tonic, "mode": mode, "num": num, "den": den, "notes": len(flat)}
        stats["segments"] += 1

def from_xml(path):
    from music21 import converter, meter
    sc = converter.parse(path)
    parts = []
    for part in sc.parts:
        ns = []
        for n in part.stripTies().flatten().notes:
            if n.duration.quarterLength > 0:
                ns += [(F(n.offset).limit_denominator(960), F(n.duration.quarterLength).limit_denominator(960), p.midi) for p in n.pitches]
        parts.append(ns)
    sigs = [(F(t.getOffsetInHierarchy(sc)).limit_denominator(960), t.numerator, t.denominator)
            for t in sc.parts[0].recurse().getElementsByClass(meter.TimeSignature)]
    return parts, sigs

def from_mid(path):
    m = mxart.read_midi(open(path, "rb").read())
    q = F(1, m["div"])
    groups = {}
    for i, tr in enumerate(m["tracks"]):
        for s, e, p, _, c in tr["notes"]:
            if c != 9: groups.setdefault((i, c), []).append((s * q, (e - s) * q, p))
    return list(groups.values()), [(t * q, n, d) for t, n, d in m["timesigs"]]

def from_tsv(path):
    """DCML note tables: one row per note head; ties are merged; the organ staff (4) doubles the violone and is left out."""
    import csv
    parts, sigs, open_ = {}, [], {}
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        if not r["quarterbeats"] or r["staff"] == "4": continue
        s, d, p, st = F(r["quarterbeats"]), F(r["duration_qb"]).limit_denominator(960), int(r["midi"]), int(r["staff"])
        n, dd = r["timesig"].split("/")
        if not sigs or sigs[-1][1:] != (int(n), int(dd)): sigs.append((s - F(r["mc_onset"]) * 4, int(n), int(dd)))
        if d <= 0: continue
        prev = open_.get((st, p))
        if r["tied"] in ("0", "-1") and prev is not None and prev[0] + prev[1] == s:
            prev[1] += d
        else:
            prev = [s, d, p]; parts.setdefault(st, []).append(prev)
        open_[(st, p)] = prev
    return [[tuple(x) for x in parts[k]] for k in sorted(parts)], sigs

if __name__ == "__main__":
    family, pattern = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 999
    meta = json.load(open(OUT + "/meta.json"))
    stats = dict(pieces=0, sig_changes=0, odd_metre=0, segments=0, failed=0)
    for path in sorted(glob.glob(pattern, recursive=True))[:limit]:
        stem = "".join(ch if ch.isalnum() else "_" for ch in os.path.basename(path).rsplit(".", 1)[0])[:40]
        try:
            parts, sigs = from_mid(path) if path.endswith(".mid") else from_tsv(path) if path.endswith(".tsv") else from_xml(path)
            write(family, stem, parts, sigs, meta, stats)
        except Exception as e:
            stats["failed"] += 1; print("failed", path, type(e).__name__, str(e)[:80])
    json.dump(meta, open(OUT + "/meta.json", "w"), indent=1)
    print(family, stats)
