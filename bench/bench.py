"""Import every tune, lint it, and (for the human tunes) inject known faults to see what the lint catches."""
import copy, glob, json, os, random, sys
from collections import Counter, defaultdict
sys.path.insert(0, "/home/user/mxart")
import mxart

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = 16
MODEL_KEYS = {"chorale": {"a1": "C major", "a2": "G major", "a3": "D minor", "a4": "A minor", "a5": "F major",
                          "b1": "Bb major", "b2": "E minor", "b3": "G minor", "b4": "D major", "b5": "A major", "c01": "C major", "c02": "A minor", "c03": "G major", "c04": "E minor", "c05": "D major", "c06": "B minor", "c07": "F major", "c08": "D minor", "c09": "Bb major", "c10": "G minor", "c11": "Eb major", "c12": "C minor", "c13": "A major", "c14": "F# minor", "c15": "E major", "c16": "F minor"},
              "chorale_hint": {"d01": "C major", "d02": "A minor", "d03": "G major", "d04": "E minor", "d05": "D major", "d06": "B minor", "d07": "F major", "d08": "D minor", "d09": "Bb major", "d10": "G minor", "d11": "Eb major", "d12": "C minor", "d13": "A major", "d14": "F# minor", "d15": "E major", "d16": "F minor"},
              "folk": {"a1": "G major", "a2": "D major", "a3": "A minor", "a4": "F major", "a5": "E minor",
                       "b1": "C major", "b2": "Bb major", "b3": "D minor", "b4": "A major", "b5": "G minor"}}
hmeta = json.load(open(HERE + "/human/meta.json"))


def load(path, key):
    data = open(path, "rb").read()
    ts = mxart.read_midi(data)["timesigs"]
    grid = (ts[0][1] if ts else 4) * 16 // (ts[0][2] if ts else 4)   # sixteenths: grid is cells per bar
    text, notes = mxart.from_midi(data, grid)
    grid_line = f"grid {grid}\n"
    text = text.replace(grid_line, grid_line + f"key {key}\n", 1)
    doc = mxart.parse(text, os.path.basename(path))
    off = next((int(n.split()[1]) for n in notes if n.startswith("WARNING:") and "off the grid" in n), 0)
    return doc, off


def codes(warn):
    return Counter(w.split()[0] for w in warn)


def corpus(source, family):
    out = []
    for path in sorted(glob.glob(f"{HERE}/{source}/{family}/*.mid")):
        stem = os.path.basename(path)[:-4]
        if source == "human":
            m = hmeta[f"{family}/{stem}.mid"]; key = f"{m['key']} {m['mode']}"
        else:
            key = MODEL_KEYS[family][stem]
        doc, off = load(path, key)
        assert not doc.errors, (path, doc.errors[:3])
        out.append((stem, doc, off))
    return out


def summarize(label, items):
    n_notes = sum(len(t.notes) for _, d, _ in items for t in d.tracks)
    off = sum(o for *_, o in items)
    per, tunes_with, total = defaultdict(list), Counter(), Counter()
    tail = 0
    for stem, doc, _ in items:
        _, warn = mxart.lint(doc, None)
        c = codes(warn)
        notes = sum(len(t.notes) for t in doc.tracks)
        for k, v in c.items():
            per[k].append(100 * v / notes); tunes_with[k] += 1; total[k] += v
        end = max(n.start + n.dur for t in doc.tracks for n in t.notes)
        tail += end % doc.grid != 0
    print(f"\n{label}: {len(items)} tunes, {n_notes} notes, {off} off-grid ({100 * off / n_notes:.1f}%), "
          f"{tail} don't end on a bar line")
    for k in sorted(total):
        print(f"  {k:<14} {total[k]:>5} total  {100 * total[k] / n_notes:6.2f} per 100 notes  in {tunes_with[k]:>2} of {len(items)} tunes")
    return {k: (total[k], n_notes, tunes_with[k], len(items)) for k in total}


# ---- fault injection, on the parsed notes
def inj_semitone(doc, rng):
    t = rng.choice([t for t in doc.tracks if t.notes]); c = [n for n in t.notes if n.dur >= 4]
    if not c: return None
    n = rng.choice(c); n.pitch += rng.choice((-1, 1)); return n.start

def inj_octave(doc, rng):
    t = rng.choice([t for t in doc.tracks if t.notes]); c = [n for n in t.notes[1:-1] if n.dur >= 2]
    if not c: return None
    n = rng.choice(c); n.pitch += rng.choice((-12, 12)); return n.start

def inj_bar_up(doc, rng):   # one voice a semitone sharp for a whole bar
    t = rng.choice([t for t in doc.tracks if t.notes]); b = rng.randrange(doc.nbars)
    hit = [n for n in t.notes if b * doc.grid <= n.start < (b + 1) * doc.grid]
    if len(hit) < 2: return None
    for n in hit: n.pitch += 1
    return b * doc.grid

def inj_flat(doc, rng):     # two bars of one voice stuck on one pitch
    t = rng.choice([t for t in doc.tracks if t.notes]); b = rng.randrange(max(1, doc.nbars - 1))
    hit = [n for n in t.notes if b * doc.grid <= n.start < (b + 2) * doc.grid]
    if len({n.pitch for n in hit}) < 3: return None
    for n in hit: n.pitch = hit[0].pitch
    return b * doc.grid

def inj_silence(doc, rng):  # a bar goes missing in every voice
    b = rng.randrange(1, max(2, doc.nbars - 1)); lo, hi = b * doc.grid, (b + 1) * doc.grid
    before = sum(len(t.notes) for t in doc.tracks)
    for t in doc.tracks: t.notes = [n for n in t.notes if not lo <= n.start < hi]
    return lo if sum(len(t.notes) for t in doc.tracks) < before else None

def inj_slip(doc, rng):     # one voice a sixteenth late for a bar
    t = rng.choice([t for t in doc.tracks if t.notes]); b = rng.randrange(doc.nbars)
    hit = [n for n in t.notes if b * doc.grid <= n.start < (b + 1) * doc.grid and n.dur >= 2]
    if len(hit) < 2: return None
    for n in hit: n.start += 1; n.dur -= 1
    return b * doc.grid

INJ = {"one note a semitone off": inj_semitone, "one note an octave off": inj_octave,
       "one voice a semitone sharp for a bar": inj_bar_up, "two bars stuck on one pitch": inj_flat,
       "a bar silent in every voice": inj_silence, "one voice a sixteenth late for a bar": inj_slip}


def injection(label, items, trials=5):
    rng = random.Random(11)
    print(f"\ninjection, {label}: caught = the lint prints a warning it didn't print for the clean tune")
    for name, fn in INJ.items():
        tried = caught = 0; by = Counter()
        for stem, doc, _ in items:
            base = Counter(mxart.lint(doc, None)[1])
            for _ in range(trials):
                d = copy.deepcopy(doc)
                if fn(d, rng) is None: continue
                tried += 1
                new = Counter(mxart.lint(d, None)[1]) - base
                if new:
                    caught += 1; by.update({w.split()[0] for w in new})
        print(f"  {name:<38} {caught:>3} of {tried:>3} ({100 * caught / max(1, tried):3.0f}%)  by {dict(by.most_common())}")


if __name__ == "__main__":
    res = {}
    for fam in ("chorale", "folk"):
        h = corpus("human", fam); m = corpus("model", fam)
        summarize(f"HUMAN {fam}", h)
        if m: summarize(f"MODEL {fam}", m)
        else: print(f"\nMODEL {fam}: not written yet")
        if "--inject" in sys.argv: injection(f"human {fam}", h)
