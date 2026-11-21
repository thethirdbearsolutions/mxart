"""Every family through the same three instruments: import coverage, the lint, part-writing parallels."""
import sys, statistics as st
from collections import Counter
sys.path.insert(0, "/home/user/mxart")
import mxart, bench, partwriting, describe

FAMS = [("human", "chorale", "Bach chorales"), ("model", "chorale", "MODEL chorales"),
        ("human", "haydn_quartets", "Haydn quartets"), ("human", "saint_georges", "Saint-Georges quartets"),
        ("human", "haydn_mutopia", "Haydn, mixed (Mutopia)"), ("human", "corelli", "Corelli trio sonatas"), ("human", "buxtehude", "Buxtehude"), ("human", "hummel", "Hummel preludes op.67"),
        ("human", "folk", "Essen folk songs"), ("model", "folk", "MODEL folk")]
print(f"{'':<26}{'pieces':>7}{'notes':>8}{'off-grid':>9}  per 100 notes: {'CLASH':>6}{'OFFKEY':>7}{'LEAP':>6}  {'MONO':>5} | per 1000 moves: {'par5':>5}{'par8':>6}")
rows = {}
for src, fam, label in FAMS:
    items = bench.corpus(src, fam)
    notes = sum(len(t.notes) for _, d, _ in items for t in d.tracks)
    off = sum(o for *_, o in items)
    c = Counter()
    for _, d, _ in items: c.update(bench.codes(mxart.lint(d, None, harmony=True)[1]))
    tot = [0] * 5
    for _, d, _ in items:
        d2 = d
        base = [t for t in d.tracks if "." not in t.name and t.notes]
        if len(base) >= 2:
            keep = d.tracks; d.tracks = base
            tot = [x + y for x, y in zip(tot, partwriting.faults(d))]
            d.tracks = keep
    p5 = f"{1000 * tot[0] / tot[3]:5.1f}" if tot[3] else "    -"
    p8 = f"{1000 * tot[1] / tot[3]:6.1f}" if tot[3] else "     -"
    print(f"{label:<26}{len(items):>7}{notes:>8}{100 * off / notes:>8.1f}%  {'':<15}{100 * c['W_CLASH'] / notes:>6.2f}{100 * c['W_OFF_KEY'] / notes:>7.2f}"
          f"{100 * c['W_LEAP'] / notes:>6.2f}  {c['W_MONOTONE']:>5} | {'':<15}{p5}{p8}")
    rows[label] = [s for _, d, _ in items for s in describe.stats(d)]
print("\nper voice, medians:")
keys = ["off-beat attacks %", "bars with a new rhythm %", "distinct note lengths", "rests (share of time) %", "repeated notes %", "leaps >= a 5th %"]
print(f"{'':<26}" + "".join(f"{k[:16]:>18}" for k in keys))
for label, ss in rows.items():
    if ss: print(f"{label:<26}" + "".join(f"{st.median(s[k] for s in ss):>18.1f}" for k in keys))
