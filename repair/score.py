"""Score each repaired chorale: parallels left (two instruments), what was changed, what else broke."""
import glob, os, sys, warnings
from collections import Counter
warnings.filterwarnings("ignore")
sys.path.insert(0, "/home/user/mxart"); sys.path.insert(0, "/home/user/mxbench")
import mxart, bench, prep
from music21 import voiceLeading, note
HERE = "/home/user/mxrepair"
V = prep.VOICES

def load(arm, stem):
    d = f"{HERE}/{arm}/{stem}"
    if arm == "C":
        p = d + "/fixed.mid"
        if not os.path.exists(p): return None, "no fixed.mid"
        try: text = prep.mx_text(p, bench.MODEL_KEYS["chorale"][stem])
        except Exception as e: return None, f"unreadable: {type(e).__name__}"
    else:
        text = open(d + "/piece.mx").read()
    doc = mxart.parse(text, stem)
    if doc.errors: return None, f"{len(doc.errors)} format error(s)"
    if sorted(t.name for t in doc.tracks) != sorted(V): return None, "voices changed: " + " ".join(t.name for t in doc.tracks)
    doc.voices = [(1, V)]
    return doc, None

def m21_parallels(doc):
    """music21 judges each pair of simultaneous attacks; only the enumeration is mine."""
    by = {t.name: {n.start: n for n in t.notes} for t in doc.tracks}
    snd = {t.name: {n.start + k: n for n in t.notes for k in range(n.dur)} for t in doc.tracks}
    held = 2 * doc.grid // doc.num
    c5 = c8 = 0
    for i, a in enumerate(V):
        for b in V[i + 1:]:
            for s in sorted(set(by[a]) & set(by[b])):
                pa, pb = snd[a].get(s - 1), snd[b].get(s - 1)
                if not pa or not pb: continue
                if min(s - pa.start, s - pb.start) >= held: continue      # after a held note: a phrase break
                q = voiceLeading.VoiceLeadingQuartet(note.Note(pa.pitch), note.Note(by[a][s].pitch), note.Note(pb.pitch), note.Note(by[b][s].pitch))
                c5 += q.parallelFifth(); c8 += q.parallelOctave() or q.parallelUnison()
    return c5 + c8

def measure(doc):
    info, warn = mxart.lint(doc, None, harmony=True)
    c = Counter((w.split()[0], "held" in w) for w in warn)
    return {"par": c[("W_PARALLEL_5TH", False)] + c[("W_PARALLEL_8VE", False)],
            "par_held": c[("W_PARALLEL_5TH", True)] + c[("W_PARALLEL_8VE", True)],
            "m21": m21_parallels(doc), "clash": c[("W_CLASH", False)], "offkey": c[("W_OFF_KEY", False)],
            "cross": c[("W_CROSSING", False)], "leap": c[("W_LEAP", False)]}

def notes(doc, only=None):
    return Counter((t.name, n.start, n.dur, n.pitch) for t in doc.tracks for n in t.notes if only in (None, t.name))

if __name__ == "__main__":
    stems = sorted(os.path.basename(p)[:-3] for p in glob.glob(HERE + "/orig/*.mx"))
    tot = {arm: Counter() for arm in "ABC"}
    print(f"{'':<5}{'before':>7} | " + " | ".join(f"{arm}: left m21 changed sop  +clash +cross" for arm in "ABC"))
    for stem in stems:
        o = mxart.parse(open(f"{HERE}/orig/{stem}.mx").read(), stem); o.voices = [(1, V)]
        mo = measure(o); row = f"{stem:<5}{mo['par']:>3}/{mo['m21']:<3} | "
        for arm in "ABC":
            doc, why = load(arm, stem)
            if doc is None:
                row += f"{why[:38]:<38} | "; tot[arm]["failed"] += 1; continue
            m = measure(doc)
            ch = sum(((notes(o) - notes(doc)) + (notes(doc) - notes(o))).values())
            sop = sum((notes(o, "soprano") - notes(doc, "soprano")).values())
            row += f"{m['par']:>7} {m['m21']:>3} {ch:>7} {sop:>3} {m['clash'] - mo['clash']:>+6} {m['cross'] - mo['cross']:>+6} | "
            t = tot[arm]; t["n"] += 1; t["left"] += m["par"]; t["m21"] += m["m21"]; t["before"] += mo["par"]; t["changed"] += ch
            t["sop"] += sop; t["clean"] += m["par"] == 0 and m["m21"] == 0; t["clash"] += m["clash"] - mo["clash"]
            t["cross"] += m["cross"] - mo["cross"]; t["held"] += m["par_held"] - mo["par_held"]; t["bars"] += doc.nbars != o.nbars
            t["leap"] += m["leap"] - mo["leap"]; t["offkey"] += m["offkey"] - mo["offkey"]
        print(row)
    print()
    for arm, name in zip("ABC", ("mxart with lint", "same text, no lint", "plain Python")):
        t = tot[arm]
        if not t["n"]: print(f"{arm} {name}: nothing scored, {t['failed']} failed"); continue
        print(f"{arm} {name:<20} scored {t['n']}, failed {t['failed']}: mid-phrase parallels {t['before']} -> {t['left']} (music21: {t['m21']}), "
              f"fully clean {t['clean']} of {t['n']}, note events changed {t['changed']} ({t['changed'] / t['n']:.1f} per piece), soprano notes changed {t['sop']}, "
              f"clashes {t['clash']:+d}, off-key lines {t['offkey']:+d}, crossings {t['cross']:+d}, leaps {t['leap']:+d}, held-note parallels {t['held']:+d}, length changed {t['bars']}")
