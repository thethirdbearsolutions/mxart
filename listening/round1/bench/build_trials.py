"""How the twelve trials were rendered (run from the repo root; paths below are as they were on the day).
Seed 77 fixes the shuffle, the sides, and where the repeats and the identical pair fall."""
import sys, random, json, subprocess, os
sys.path.insert(0, "."); import mxart
R = "repair"; rng = random.Random(77)
def load(s, which):
    d = mxart.parse(open(f"{R}/orig/{s}.mx" if which == "orig" else f"{R}/A/{s}/piece.mx").read(), s)
    d.tempo = 76
    for t in d.tracks: t.program, t.vel = 19, 90
    return d
stems = ["a2", "c01", "c03", "c04", "c05", "c06", "c07", "c09", "c10"]
items = [dict(stem=s, kind="pair", sides=rng.sample(["orig", "fixed"], 2)) for s in stems]
rng.shuffle(items)
first = {it["stem"]: it["sides"] for it in items}
extra = [dict(stem="a2", kind="repeat", sides=first["a2"][::-1]), dict(stem="c09", kind="repeat", sides=first["c09"][::-1]),
         dict(stem="c05", kind="identical", sides=["orig", "orig"])]
order = items[:]
for e in extra:
    while True:
        pos = rng.randrange(6, len(order) + 1)
        if e["stem"] not in [order[i]["stem"] for i in (pos - 1, pos) if 0 <= i < len(order)]: order.insert(pos, e); break
os.makedirs("out/audio", exist_ok=True)
for i, it in enumerate(order, 1):
    for letter, which in zip("xy", it["sides"]):
        wav = f"out/audio/t{i:02d}{letter}.wav"
        mxart.to_wav(load(it["stem"], which), wav)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", "aecho=0.8:0.6:70|130:0.22|0.12,volume=0.9", "-ac", "1", "-b:a", "96k", wav[:-4] + ".mp3"], check=True)
        os.remove(wav)
