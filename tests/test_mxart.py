"""Run: python3 -m pytest tests/ -q   (or python3 tests/test_mxart.py)"""
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import mxart

EX = os.path.join(ROOT, "examples")


def run(*args):
    p = subprocess.run([sys.executable, os.path.join(ROOT, "mxart.py"), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def codes(path):
    return [e.split(": ")[1].split(" ")[0] for _, e in mxart.load(path).errors]


def test_examples_check():
    assert mxart.load(os.path.join(EX, "tune.mx")).errors == []
    assert mxart.load(os.path.join(EX, "dull.mx")).errors == []


def test_broken_reports_every_error_at_once():
    assert codes(os.path.join(EX, "broken.mx")) == [
        "E_BAR_LENGTH", "E_BAD_NOTE", "E_HOLD", "E_HOLD", "E_BAD_OPT", "E_TRACK_LENGTH", "E_UNKNOWN_KEY"]
    rc, out = run("check", os.path.join(EX, "broken.mx"))
    assert rc == 1 and "broken.mx:9: E_BAR_LENGTH (track lead, bar 1): bar is 7 cells, expected 8" in out


def test_notes_holds_chords_and_ties_across_bars():
    doc = mxart.parse("grid 4\n@track a\n| C4 - . E4+G4 |\n| - - C4! . |\n", "t")
    assert doc.errors == []
    got = sorted((n.start, n.dur, n.pitch, n.accent) for n in doc.tracks[0].notes)
    assert got == [(0, 2, 60, False), (3, 3, 64, False), (3, 3, 67, False), (6, 1, 60, True)]


def test_lint_finds_what_dull_is_made_of():
    info, warn = mxart.lint(mxart.load(os.path.join(EX, "dull.mx")))
    assert {w.split()[0] for w in warn} == {"W_LEAP", "W_MONOTONE", "W_RANGE"}
    assert any("not listed: 1 line(s) of notes outside the key, 3 semitone clash(es), 0 voice crossing(s)" in i for i in info)
    _, warn = mxart.lint(mxart.load(os.path.join(EX, "dull.mx")), harmony=True)
    kinds = {w.split()[0] for w in warn}
    assert kinds == {"W_CLASH", "W_LEAP", "W_MONOTONE", "W_OFF_KEY", "W_RANGE"}
    assert any("15 of 24 notes (62%) are E5" in w for w in warn)
    assert any("bar 3 beat 1, on the beat" in w and "minor 2nd/9th" in w for w in warn)


PARTS = """grid 4
@voices s a t b
@track s
| A4 B4 C5 - | C5 - - - |
@track a
| F4 G4 E4 - | E4 - - - |
@track t
| F3 G3 C4 - | G4 - C4 - |
@track b
| D3 E3 C3 - | C3 - - - |
"""


def test_part_writing_is_only_checked_for_a_voices_group():
    doc = mxart.parse(PARTS, "t")
    assert doc.errors == []
    assert "W_CROSSING (bar 2 beat 1): t G4 is above a E4, for 2 cell(s)" in mxart.lint(doc, harmony=True)[1]
    assert mxart.lint(doc)[1] == [
        "W_PARALLEL_5TH (bar 1 beat 2): s and b move A4/D3 to B4/E3",
        "W_PARALLEL_8VE (bar 1 beat 2): a and t move F4/F3 to G4/G3"]
    doc.voices = []
    assert mxart.lint(doc)[1] == []


def test_voices_must_name_tracks():
    doc = mxart.parse("grid 4\n@voices s nope\n@track s\n| C4 - - - |\n", "t")
    assert [e.split(": ")[1].split(" ")[0] for _, e in doc.errors] == ["E_VOICES"]


def test_lint_names_transposed_bars():
    info, _ = mxart.lint(mxart.load(os.path.join(EX, "tune.mx")))
    assert any("bar 3 = bar 1 +5, bar 4 = bar 1 +7, bar 5 = bar 1" in line for line in info)


def test_round_trip_is_lossless():
    with tempfile.TemporaryDirectory() as d:
        mid, back = os.path.join(d, "t.mid"), os.path.join(d, "back.mx")
        src = os.path.join(EX, "tune.mx")
        assert run("render", src, "-o", mid)[0] == 0
        assert run("cmp", src, mid) == (0, "same: 192 notes\n")
        rc, out = run("import", mid, "-o", back, "--grid", "8")
        assert rc == 0 and "WARNING" not in out
        assert run("cmp", src, back)[0] == 0
        mid2 = os.path.join(d, "t2.mid")
        run("render", back, "-o", mid2)
        assert open(mid, "rb").read() == open(mid2, "rb").read()   # byte for byte, second time round


def test_import_says_when_the_grid_is_too_coarse():
    with tempfile.TemporaryDirectory() as d:
        mid, back = os.path.join(d, "t.mid"), os.path.join(d, "back.mx")
        run("render", os.path.join(EX, "tune.mx"), "-o", mid)
        rc, out = run("import", mid, "-o", back, "--grid", "4")
        assert "129 of 192 notes were off the grid" in out
        assert run("cmp", os.path.join(EX, "tune.mx"), back)[0] == 1


def test_import_splits_overlapping_notes_into_voices():
    # one channel, a held C4 under a moving line: not one row's worth
    ev = [(0, 2, bytes([0x90, 60, 90])), (1920, 1, bytes([0x80, 60, 0]))]
    for i, p in enumerate((72, 74, 76, 77)):
        ev += [(i * 480, 2, bytes([0x90, p, 90])), ((i + 1) * 480, 1, bytes([0x80, p, 0]))]
    data = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 1, 0, 1, 1, 0xE0]) + mxart.chunk(ev)
    text, notes = mxart.from_midi(data, 4)
    doc = mxart.parse(text, "t")
    assert doc.errors == [] and len(doc.tracks) == 2
    assert sorted((n.start, n.dur, n.pitch) for t in doc.tracks for n in t.notes) == [
        (0, 1, 72), (0, 4, 60), (1, 1, 74), (2, 1, 76), (3, 1, 77)]


def test_roll_has_rulers_and_marks_off_key_rows():
    out = mxart.roll(mxart.load(os.path.join(EX, "dull.mx")))
    assert "      1.2.3.4. 1.2.3.4. 1.2.3.4. 1.2.3.4." in out
    assert " F#5~ ........|......A.|" in out
    assert "   E5 AAAAAa.A|AAAAAa.A|......A.|Aa..Aaaa" in out


def test_every_warning_the_lint_can_print_has_an_entry():
    import re
    src = open(os.path.join(ROOT, "mxart.py")).read()
    printed = set(re.findall(r'"\'?(W_[A-Z0-9_]+)', src.split("# ---------------------------------------------------------------- the knowledge base")[0]))
    assert printed and printed <= set(mxart.KB), printed - set(mxart.KB)


def test_explain_and_brief():
    rc, out = run("explain", "w_parallel_5th")
    assert rc == 0 and "Bach chorales 0.7" in out and "say this in the brief: Avoid parallel fifths" in out
    assert run("explain", "W_NOPE")[0] == 1
    rc, out = run("brief", "--kind", "parts")
    assert out.splitlines()[0] == "Avoid parallel fifths and parallel octaves between voices." and len(out.splitlines()) == 3
    assert run("brief", "--kind", "melody")[1].strip() == ""       # nothing measured for a single line yet


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("ok", k)
