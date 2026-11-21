"""Set up the three repair arms for each faulty model chorale."""
import os, shutil, sys
sys.path.insert(0, "/home/user/mxart"); sys.path.insert(0, "/home/user/mxbench")
import mxart, bench
HERE = "/home/user/mxrepair"
VOICES = ["soprano", "alto", "tenor", "bass"]

def mx_text(path, key):
    data = open(path, "rb").read()
    ts = mxart.read_midi(data)["timesigs"]
    grid = ts[0][1] * 16 // ts[0][2]
    text, _ = mxart.from_midi(data, grid)
    return text.replace(f"grid {grid}\n", f"grid {grid}\nkey {key}\n@voices {' '.join(VOICES)}\n", 1)

README_A = open("/home/user/mxart/README.md").read()
README_B = """# mx: music as text

A tune is a plain-text grid. `grid 16` in 4/4 means sixteen cells per bar, so each cell is a sixteenth.
In a bar row a note is `C5`, `-` holds the note before it, `.` is a rest. Every bar must have exactly
`grid` cells.

Commands:
- `python3 mx.py check piece.mx`   format errors, each with a code and location
- `python3 mx.py roll piece.mx`    a text piano roll with bar and beat rulers
- `python3 mx.py render piece.mx -o piece.mid`
"""

def faulty():
    out = []
    for stem, doc, _ in bench.corpus("model", "chorale"):
        if sorted(t.name for t in doc.tracks) != sorted(VOICES): continue
        doc.voices = [(1, VOICES)]
        w = [x for x in mxart.lint(doc, None)[1] if x.startswith("W_PARALLEL")]
        mid = [x for x in w if "held" not in x]
        if mid: out.append((stem, len(mid), len(w)))
    return out

if __name__ == "__main__":
    f = faulty()
    print(len(f), "faulty of", len(bench.corpus("model", "chorale")), f)
    for stem, *_ in f:
        src = f"/home/user/mxbench/model/chorale/{stem}.mid"
        text = mx_text(src, bench.MODEL_KEYS["chorale"][stem])
        for arm in "ABC":
            d = f"{HERE}/{arm}/{stem}"; os.makedirs(d, exist_ok=True)
            if arm == "C":
                shutil.copy(src, d + "/piece.mid")
            else:
                open(d + "/piece.mx", "w").write(text)
                shutil.copy("/home/user/mxart/mxart.py" if arm == "A" else HERE + "/mx_nolint.py", d + ("/mxart.py" if arm == "A" else "/mx.py"))
                open(d + "/README.md", "w").write(README_A if arm == "A" else README_B)
        os.makedirs(f"{HERE}/orig", exist_ok=True); open(f"{HERE}/orig/{stem}.mx", "w").write(text)
