#!/usr/bin/env python3
"""mxart: music as text. A prototype of "pxart for MIDI".

A tune is a plain-text grid: one cell per step, one row of bars per track.

    mxart 1
    tempo 112
    time 4/4
    grid 8                      cells per bar
    key C major                 optional: turns on the off-key lint
    k 36                        drum palette: one char, then a GM drum note

    @track lead program=80
    | E5 -  G5 E5 C5 -  D5 E5 |     a note, '-' holds it, '.' is a rest
    @track pad program=89
    | C4+E4+G4 - - - - - - - |      '+' joins a chord
    @drums kick
    | k...k... |                    drum rows: one palette char per cell

Commands: check, roll, render, import, cmp. Python 3.9+; --wav needs numpy.
"""
import argparse
import math
import re
import struct
import sys
from collections import Counter
from itertools import combinations
from fractions import Fraction

PPQ = 480
NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10, 11]}  # minor allows the raised 7th
FLAT_KEYS = {("F", "major"), ("Bb", "major"), ("Eb", "major"), ("Ab", "major"), ("Db", "major"), ("Gb", "major"),
             ("D", "minor"), ("G", "minor"), ("C", "minor"), ("F", "minor"), ("Bb", "minor"), ("Eb", "minor")}
DEGREES = {0: "tonic", 7: "5th", 4: "3rd", 3: "3rd", 2: "2nd", 5: "4th", 9: "6th", 8: "6th", 11: "7th", 10: "7th"}
DRUM_KEYS = {35: "K", 36: "k", 37: "r", 38: "s", 39: "p", 40: "S", 42: "h", 44: "f", 46: "o", 49: "c", 51: "d",
             41: "t", 43: "u", 45: "v", 47: "w", 48: "y", 50: "z"}
RESERVED = set(".-|#@+!")


def midi_of(tok):
    m = NOTE_RE.match(tok)
    if not m:
        return None
    n = 12 * (int(m.group(3)) + 1) + PC[m.group(1).upper()] + {"#": 1, "b": -1, "": 0}[m.group(2)]
    return n if 0 <= n <= 127 else None


def name_of(n, flats=False):
    return f"{(FLAT if flats else SHARP)[n % 12]}{n // 12 - 1}"


class Note:
    __slots__ = ("start", "dur", "pitch", "accent", "bar", "cell", "line")

    def __init__(self, start, dur, pitch, accent, bar, cell, line):
        self.start, self.dur, self.pitch, self.accent, self.bar, self.cell, self.line = start, dur, pitch, accent, bar, cell, line


class Track:
    def __init__(self, kind, name, line):
        self.kind, self.name, self.line = kind, name, line
        self.program, self.vel, self.range = 0, 96, None
        self.bars = []    # (line, [cells])
        self.notes = []


class Doc:
    def __init__(self, path):
        self.path = path
        self.tempo, self.num, self.den, self.grid = 120, 4, 4, 16
        self.key = None   # (tonic pc, mode, name)
        self.palette = {}
        self.voices = []  # (line, [track names, highest first]): groups checked for part-writing
        self.tracks = []
        self.errors = []
        self.nbars = 0

    def err(self, code, line, msg, track=None, bar=None, cell=None):
        where = ", ".join(x for x in (track and f"track {track}", bar and f"bar {bar}", cell and f"cell {cell}") if x)
        self.errors.append((line, f"{self.path}:{line}: {code}{f' ({where})' if where else ''}: {msg}"))

    @property
    def cell_ticks(self):
        return Fraction(PPQ * 4 * self.num, self.den * self.grid)

    @property
    def flats(self):
        return bool(self.key) and (self.key[2], self.key[1]) in FLAT_KEYS

    def in_key(self, pitch):
        return self.key is None or (pitch - self.key[0]) % 12 in SCALES[self.key[1]]

    def where(self, cell_abs):
        """'bar 3 beat 2' (or 'bar 3 beat 2+1' off the beat) for an absolute cell."""
        bar, c = cell_abs // self.grid + 1, cell_abs % self.grid
        if self.grid % self.num:
            return f"bar {bar} cell {c + 1}"
        cpb = self.grid // self.num
        return f"bar {bar} beat {c // cpb + 1}" + (f"+{c % cpb}/{cpb}" if c % cpb else "")

    def on_beat(self, cell_abs):
        return self.grid % self.num == 0 and (cell_abs % self.grid) % (self.grid // self.num) == 0


def parse(text, path):
    doc, cur = Doc(path), None
    for i, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        w = line.split()
        if line.startswith("|"):
            if cur is None:
                doc.err("E_ORDER", i, "a bar row before any @track or @drums line")
                continue
            if not line.endswith("|") or len(line) < 2:
                doc.err("E_BAD_ROW", i, "a bar row starts and ends with '|'", cur.name)
                continue
            for seg in line[1:-1].split("|"):
                cells = seg.split() if cur.kind == "track" else list("".join(seg.split()))
                cur.bars.append((i, cells))
        elif w[0] in ("@track", "@drums"):
            if len(w) < 2 or "=" in w[1]:
                doc.err("E_BAD_TRACK", i, f"{w[0]} needs a name: {w[0]} lead program=80")
                continue
            if any(t.name == w[1] for t in doc.tracks):
                doc.err("E_DUP_TRACK", i, f"track '{w[1]}' is already defined")
            cur = Track(w[0][1:], w[1], i)
            doc.tracks.append(cur)
            for opt in w[2:]:
                k, _, v = opt.partition("=")
                if k == "program" and v.isdigit() and int(v) < 128 and cur.kind == "track":
                    cur.program = int(v)
                elif k == "vel" and v.isdigit() and 0 < int(v) < 128:
                    cur.vel = int(v)
                elif k == "range" and cur.kind == "track" and len(r := [midi_of(x) for x in v.split("..")]) == 2 and None not in r:
                    cur.range = tuple(r)
                else:
                    doc.err("E_BAD_OPT", i, f"'{opt}': options are program=0..127, vel=1..127, range=C3..C6", cur.name)
        elif w[0] == "@voices":
            doc.voices.append((i, w[1:]))
        elif w[0] == "mxart":
            if w[1:] != ["1"]:
                doc.err("E_VERSION", i, "this reader knows 'mxart 1'")
        elif w[0] == "tempo" and len(w) == 2 and w[1].isdigit() and 20 <= int(w[1]) <= 400:
            doc.tempo = int(w[1])
        elif w[0] == "time" and len(w) == 2 and re.fullmatch(r"\d+/(1|2|4|8|16)", w[1]) and int(w[1].split("/")[0]) > 0:
            doc.num, doc.den = map(int, w[1].split("/"))
        elif w[0] == "grid" and len(w) == 2 and w[1].isdigit() and int(w[1]) > 0:
            doc.grid = int(w[1])
        elif w[0] == "key" and len(w) == 3 and w[2] in SCALES and midi_of(w[1] + "4") is not None:
            doc.key = (midi_of(w[1] + "4") % 12, w[2], w[1][0].upper() + w[1][1:])
        elif len(w) == 2 and len(w[0]) == 1 and w[0] not in RESERVED and (w[1].isdigit() and int(w[1]) < 128):
            if w[0] in doc.palette:
                doc.err("E_DUP_KEY", i, f"drum key '{w[0]}' is already defined")
            doc.palette[w[0]] = int(w[1])
        elif w[0] in ("tempo", "time", "grid", "key"):
            doc.err("E_HEADER", i, {"tempo": "tempo 20..400", "time": "time N/D with D one of 1 2 4 8 16",
                                    "grid": "grid N (cells per bar)", "key": "key C major | key F# minor"}[w[0]]
                    + f", not '{line}'")
        else:
            doc.err("E_BAD_LINE", i, f"not a header, a drum key, a track or a bar row: '{line[:40]}'")
    if doc.cell_ticks.denominator != 1:
        doc.err("E_GRID", 1, f"grid {doc.grid} in {doc.num}/{doc.den} gives a cell of {float(doc.cell_ticks):.2f} ticks; "
                             f"pick a grid that divides {PPQ * 4 * doc.num // doc.den}")
    if not doc.tracks:
        doc.err("E_NO_TRACKS", 1, "no @track or @drums")
    for line, names in doc.voices:
        bad = [n for n in names if not any(t.name == n and t.kind == "track" for t in doc.tracks)]
        if bad or len(names) < 2 or len(set(names)) != len(names):
            doc.err("E_VOICES", line, "@voices lists two or more @track names, highest voice first"
                    + (f"; not a track: {' '.join(bad)}" if bad else ""))
    compile_notes(doc)
    doc.errors.sort()
    return doc


def compile_notes(doc):
    g = doc.grid
    for t in doc.tracks:
        open_ = None   # [start, pitches, accent, bar, cell, line]

        def close(at):
            nonlocal open_
            if open_:
                for p in open_[1]:
                    t.notes.append(Note(open_[0], at - open_[0], p, open_[2], open_[3], open_[4], open_[5]))
            open_ = None

        for b, (line, cells) in enumerate(t.bars):
            if len(cells) != g:
                doc.err("E_BAR_LENGTH", line, f"bar is {len(cells)} cells, expected {g}", t.name, b + 1)
            for j, tok in enumerate(cells[:g]):
                at = b * g + j
                if t.kind == "drums":
                    if tok == ".":
                        continue
                    if tok not in doc.palette:
                        doc.err("E_UNKNOWN_KEY", line, f"'{tok}' isn't a drum key (defined: "
                                f"{' '.join(doc.palette) or 'none'})", t.name, b + 1, j + 1)
                    else:
                        t.notes.append(Note(at, 1, doc.palette[tok], False, b + 1, j + 1, line))
                elif tok == "-":
                    if open_ is None:
                        doc.err("E_HOLD", line, "'-' holds a note, but nothing is sounding", t.name, b + 1, j + 1)
                elif tok == ".":
                    close(at)
                else:
                    close(at)
                    accent = tok.endswith("!")
                    pitches = [midi_of(x) for x in tok.rstrip("!").split("+")]
                    if None in pitches:
                        doc.err("E_BAD_NOTE", line, f"'{tok}' isn't a note (C4, F#3, Bb5), a chord (C4+E4+G4), "
                                "'-' or '.'", t.name, b + 1, j + 1)
                    else:
                        open_ = [at, sorted(set(pitches)), accent, b + 1, j + 1, line]
            if len(cells) < g:
                close(b * g + len(cells))
        close(len(t.bars) * g)
    doc.nbars = max((len(t.bars) for t in doc.tracks), default=0)
    for t in doc.tracks:
        if len(t.bars) != doc.nbars:
            doc.err("E_TRACK_LENGTH", t.line, f"{len(t.bars)} bars, but the longest track has {doc.nbars}", t.name)
    if sum(t.kind == "track" for t in doc.tracks) > 15:
        doc.err("E_TRACKS", 1, "more than 15 pitched tracks (one MIDI channel each)")


def load(path):
    with open(path, encoding="utf-8") as f:
        return parse(f.read(), path)


def load_ok(path):
    doc = load(path)
    if doc.errors:
        for _, e in doc.errors:
            print(e, file=sys.stderr)
        sys.exit(f"{path}: {len(doc.errors)} error(s); fix these first")
    return doc


# ---------------------------------------------------------------- MIDI out / in

def vlq(n):
    out = [n & 0x7F]
    while n > 0x7F:
        n >>= 7
        out.append((n & 0x7F) | 0x80)
    return bytes(reversed(out))


def chunk(events):
    """events: (tick, order, bytes) -> an MTrk chunk."""
    data, last = b"", 0
    for tick, _, ev in sorted(events, key=lambda e: (e[0], e[1])):
        data += vlq(tick - last) + ev
        last = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def channels(doc):
    free = [c for c in range(16) if c != 9]
    return {t.name: 9 if t.kind == "drums" else free.pop(0) for t in doc.tracks}


def to_midi(doc):
    ct, ch = int(doc.cell_ticks), channels(doc)
    meta = [(0, 0, b"\xff\x58\x04" + bytes([doc.num, int(math.log2(doc.den)), 24, 8])),
            (0, 0, b"\xff\x51\x03" + struct.pack(">I", round(60_000_000 / doc.tempo))[1:])]
    chunks = [chunk(meta)]
    for t in doc.tracks:
        c = ch[t.name]
        ev = [(0, 0, b"\xff\x03" + vlq(len(t.name.encode())) + t.name.encode())]
        if t.kind == "track":
            ev.append((0, 0, bytes([0xC0 | c, t.program])))
        for n in t.notes:
            vel = min(127, t.vel + 24) if n.accent else t.vel
            ev.append((n.start * ct, 2, bytes([0x90 | c, n.pitch, vel])))
            ev.append(((n.start + n.dur) * ct, 1, bytes([0x80 | c, n.pitch, 0])))
        chunks.append(chunk(ev))
    return b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), PPQ) + b"".join(chunks)


def read_midi(data):
    if data[:4] != b"MThd":
        raise ValueError("not a MIDI file (no MThd)")
    _, ntrk, div = struct.unpack(">HHH", data[8:14])
    if div & 0x8000:
        raise ValueError("SMPTE time division isn't supported")
    out = {"div": div, "tempos": [], "timesigs": [], "tracks": []}
    pos = 8 + struct.unpack(">I", data[4:8])[0]
    for _ in range(ntrk):
        if data[pos:pos + 4] != b"MTrk":
            raise ValueError("bad track chunk")
        end = pos + 8 + struct.unpack(">I", data[pos + 4:pos + 8])[0]
        p, tick, status = pos + 8, 0, 0
        tr = {"name": None, "notes": [], "programs": {}}
        on = {}
        while p < end:
            d = 0
            while True:
                b = data[p]; p += 1
                d = (d << 7) | (b & 0x7F)
                if not b & 0x80:
                    break
            tick += d
            b = data[p]
            if b == 0xFF:
                kind = data[p + 1]; p += 2
                ln = 0
                while True:
                    x = data[p]; p += 1
                    ln = (ln << 7) | (x & 0x7F)
                    if not x & 0x80:
                        break
                body = data[p:p + ln]; p += ln
                if kind == 0x51:
                    out["tempos"].append((tick, int.from_bytes(body, "big")))
                elif kind == 0x58:
                    out["timesigs"].append((tick, body[0], 2 ** body[1]))
                elif kind == 0x03 and tr["name"] is None:
                    tr["name"] = body.decode("utf-8", "replace")
            elif b in (0xF0, 0xF7):
                p += 1
                ln = 0
                while True:
                    x = data[p]; p += 1
                    ln = (ln << 7) | (x & 0x7F)
                    if not x & 0x80:
                        break
                p += ln
            else:
                if b & 0x80:
                    status = b; p += 1
                hi, c = status & 0xF0, status & 0x0F
                a = data[p]; p += 1
                if hi not in (0xC0, 0xD0):
                    v = data[p]; p += 1
                if hi == 0x90 and v:
                    on.setdefault((c, a), []).append((tick, v))
                elif hi == 0x80 or hi == 0x90:
                    if on.get((c, a)):
                        s, vel = on[(c, a)].pop(0)
                        tr["notes"].append((s, tick, a, vel, c))
                elif hi == 0xC0:
                    tr["programs"].setdefault(c, a)
        out["tracks"].append(tr)
        pos = end
    return out


def note_set(path):
    """Every note as (drums?, program, start, dur, pitch), in 480ths of a quarter: what cmp compares."""
    if path.endswith((".mid", ".midi")):
        with open(path, "rb") as f:
            m = read_midi(f.read())
        k = Fraction(PPQ, m["div"])
        return sorted((c == 9, 0 if c == 9 else tr["programs"].get(c, 0), s * k, (e - s) * k, p)
                      for tr in m["tracks"] for s, e, p, _, c in tr["notes"])
    doc, ct = load_ok(path), None
    ct = doc.cell_ticks
    return sorted((t.kind == "drums", t.program if t.kind == "track" else 0, n.start * ct, n.dur * ct, n.pitch)
                  for t in doc.tracks for n in t.notes)


def from_midi(data, grid):
    m = read_midi(data)
    num, den = (m["timesigs"][0][1:] if m["timesigs"] else (4, 4))
    tempo = round(60_000_000 / m["tempos"][0][1]) if m["tempos"] else 120
    cell = Fraction(m["div"] * 4 * num, den * grid)
    notes_out, off, total, worst = [], 0, 0, 0
    lines = ["mxart 1", f"tempo {tempo}", f"time {num}/{den}", f"grid {grid}", ""]
    groups = []   # (name, channel, program, [(start, dur, pitch, vel)])
    for i, tr in enumerate(m["tracks"]):
        for c in sorted({n[4] for n in tr["notes"]}):
            q = []
            for s, e, p, vel, cc in tr["notes"]:
                if cc != c:
                    continue
                qs, qd = round(s / cell), max(1, round((e - s) / cell))
                total += 1
                if qs * cell != s or qd * cell != e - s:
                    off += 1
                    worst = max(worst, abs(float(qs * cell - s)), abs(float(qd * cell - (e - s))))
                q.append((qs, qd, p, vel))
            groups.append((re.sub(r"[^A-Za-z0-9_.-]", "_", tr["name"] or f"t{i}") or f"t{i}", c, tr["programs"].get(c, 0), q))
    nbars = max((math.ceil((s + d) / grid) for g in groups for s, d, _, _ in g[3]), default=1)
    palette, body, used = {}, [], set()

    def uniq(name):
        base, k = name, 2
        while name in used:
            name, k = f"{base}.{k}", k + 1
        used.add(name)
        return name

    for name, c, prog, q in groups:
        vel = sorted(v for *_, v in q)[len(q) // 2]
        if c == 9:
            pitches = sorted({p for _, _, p, _ in q})
            for pitch in pitches:
                key = DRUM_KEYS.get(pitch)
                if key is None or palette.get(key, pitch) != pitch:
                    key = next(ch for ch in "abcdefgijlmnqxABCDEFGHIJLMNOPQRTUVWXYZ0123456789" if ch not in palette)
                palette[key] = pitch
                row = ["."] * (nbars * grid)
                for s, _, p, _ in q:
                    if p == pitch:
                        row[s] = key
                body += ["", f"@drums {uniq(name if len(pitches) == 1 else f'{name}.{key}')} vel={vel}"]
                body += ["| " + "".join(row[b * grid:(b + 1) * grid]) + " |" for b in range(nbars)]
            continue
        chords = {}
        for s, d, p, v in q:
            chords.setdefault((s, d), []).append((p, v))
        voices = []   # (free_at, [cells])
        for (s, d), ps in sorted(chords.items()):
            v = next((v for v in voices if v[0] <= s), None)
            if v is None:
                v = [0, ["."] * (nbars * grid)]
                voices.append(v)
            accent = "!" if sum(x[1] for x in ps) / len(ps) > vel + 15 else ""
            v[1][s] = "+".join(name_of(p) for p in sorted({x[0] for x in ps})) + accent
            for k in range(s + 1, s + d):
                v[1][k] = "-"
            v[0] = s + d
        for k, v in enumerate(voices):
            w = max(len(x) for x in v[1])
            body += ["", f"@track {uniq(name if k == 0 else f'{name}.{k + 1}')} program={prog} vel={vel}"]
            body += ["| " + " ".join(x.ljust(w) for x in v[1][b * grid:(b + 1) * grid]) + " |" for b in range(nbars)]
    lines += [f"{k} {p}" for k, p in sorted(palette.items(), key=lambda kv: kv[1])] + body
    notes_out.append(f"imported {total} notes, {len(groups)} channel(s), {nbars} bars at grid {grid}")
    if off:
        notes_out.append(f"WARNING: {off} of {total} notes were off the grid and moved (worst by {worst:.0f} ticks of "
                         f"{m['div']} per quarter); try a finer --grid")
    if len(m["tempos"]) > 1 or len(m["timesigs"]) > 1:
        notes_out.append("WARNING: the file changes tempo or time signature; only the first is kept")
    return "\n".join(lines) + "\n", notes_out


# ---------------------------------------------------------------- looking: the text piano roll

def roll(doc, per_line=4, full=False):
    pitched = [t for t in doc.tracks if t.kind == "track"]
    drums = [t for t in doc.tracks if t.kind == "drums"]
    g, out = doc.grid, []
    letters = {t.name: chr(65 + i) for i, t in enumerate(pitched)}
    cellmap = {}
    for t in pitched:
        L = letters[t.name]
        for n in t.notes:
            for k in range(n.dur):
                key = (n.pitch, n.start + k)
                ch = L if k == 0 else L.lower()
                cellmap[key] = ch if key not in cellmap or cellmap[key].upper() == L else "*"
    used = sorted({p for p, _ in cellmap}, reverse=True)
    rows = list(range(used[0], used[-1] - 1, -1)) if full and used else used
    out.append("  ".join(f"{letters[t.name]}={t.name}" for t in pitched) + "   UPPER = attack, lower = held, * = two tracks"
               + ("   ~ = not in key" if doc.key else ""))
    cpb = g // doc.num if g % doc.num == 0 else None
    for b0 in range(0, doc.nbars, per_line):
        bars = range(b0, min(b0 + per_line, doc.nbars))
        out.append("")
        out.append("      " + " ".join(f"{b + 1:<{g}}" for b in bars))
        out.append("      " + " ".join("".join(str(j // cpb + 1) if cpb and j % cpb == 0 else "." for j in range(g)) for b in bars))
        prev = None
        for p in rows:
            if prev is not None and prev - p > 1:
                out.append("    :")
            prev = p
            label = name_of(p, doc.flats) + ("" if doc.in_key(p) else "~")
            out.append(f"{label:>5} " + "|".join("".join(cellmap.get((p, b * g + j), ".") for j in range(g)) for b in bars))
        for t in drums:
            hits = {n.start: next((k for k, v in doc.palette.items() if v == n.pitch), "x") for n in t.notes}
            out.append(f"{t.name[:5]:>5} " + "|".join("".join(hits.get(b * g + j, ".") for j in range(g)) for b in bars))
    return "\n".join(out)


# ---------------------------------------------------------------- a plain synth, so a person can listen

def to_wav(doc, path, sr=22050):
    import numpy as np
    import wave
    spc = float(doc.cell_ticks) / PPQ * 60 / doc.tempo   # seconds per cell
    mix = np.zeros(int((doc.nbars * doc.grid * spc + 1.0) * sr))
    rng = np.random.default_rng(1)
    for ti, t in enumerate(doc.tracks):
        for n in t.notes:
            i0 = int(n.start * spc * sr)
            amp = (min(127, t.vel + 24) if n.accent else t.vel) / 127
            if t.kind == "drums":
                if n.pitch in (35, 36):
                    x = np.arange(int(0.20 * sr)) / sr
                    sig = np.sin(2 * np.pi * (45 * x + 75 / 18 * (1 - np.exp(-18 * x)))) * np.exp(-14 * x) * 1.4
                elif n.pitch in (38, 40, 37, 39):
                    x = np.arange(int(0.16 * sr)) / sr
                    sig = (rng.standard_normal(len(x)) * 0.7 + np.sin(2 * np.pi * 185 * x) * 0.5) * np.exp(-22 * x)
                else:
                    x = np.arange(int((0.25 if n.pitch in (46, 49, 51) else 0.05) * sr)) / sr
                    noise = rng.standard_normal(len(x))
                    sig = np.diff(noise, prepend=0) * np.exp(-x * (12 if len(x) > 0.1 * sr else 70)) * 0.35
            else:
                f = 440 * 2 ** ((n.pitch - 69) / 12)
                x = np.arange(int((n.dur * spc + 0.05) * sr)) / sr
                bass = 32 <= t.program <= 39 or n.pitch < 48
                harm = [(1, 1.0), (2, 0.35), (3, 0.12)] if bass else [(1, 1.0), (3, 0.33), (5, 0.2), (7, 0.1)]
                sig = sum(a * np.sin(2 * np.pi * f * h * x) for h, a in harm if f * h < sr / 2)
                dur = n.dur * spc
                env = np.minimum(1, x / 0.006) * (0.55 + 0.45 * np.exp(-5 * x)) * np.clip((dur + 0.04 - x) / 0.04, 0, 1)
                sig = sig * env * (0.5 if bass else 0.28)
            mix[i0:i0 + len(sig)] += sig[:len(mix) - i0] * amp
    mix = mix / max(1e-9, np.abs(mix).max()) * 0.85
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


# ---------------------------------------------------------------- commands

def main(argv=None):
    ap = argparse.ArgumentParser(prog="mxart", description="Music as text: check it, look at it, render it.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check", help="format errors, each with a code and a location; exit 1 on any")
    p.add_argument("files", nargs="+")
    p = sub.add_parser("roll", help="a text piano roll with bar and beat rulers")
    p.add_argument("file"); p.add_argument("--bars", type=int, default=4, help="bars per line (default 4)")
    p.add_argument("--full", action="store_true", help="a row for every semitone, not only the pitches used")
    p = sub.add_parser("render", help="write a .mid (and --wav, a plain synth, to listen)")
    p.add_argument("file"); p.add_argument("-o", required=True); p.add_argument("--wav")
    p = sub.add_parser("import", help="a .mid as .mx text, quantized to --grid")
    p.add_argument("file"); p.add_argument("-o", required=True); p.add_argument("--grid", type=int, default=16)
    p = sub.add_parser("cmp", help="do two files (.mx or .mid) hold the same notes? velocities aren't compared")
    p.add_argument("a"); p.add_argument("b")
    a = ap.parse_args(argv)

    if a.cmd == "check":
        bad = 0
        for f in a.files:
            doc = load(f)
            for _, e in doc.errors:
                print(e)
            bad += bool(doc.errors)
            if doc.errors:
                print(f"FAIL {f}: {len(doc.errors)} error(s)")
            else:
                print(f"ok   {f}: {len(doc.tracks)} tracks, {doc.nbars} bars, {sum(len(t.notes) for t in doc.tracks)} notes")
        return 1 if bad else 0
    if a.cmd == "roll":
        print(roll(load_ok(a.file), a.bars, a.full))
        return 0
    if a.cmd == "render":
        doc = load_ok(a.file)
        data = to_midi(doc)
        with open(a.o, "wb") as f:
            f.write(data)
        print(f"wrote {a.o}: {len(data)} bytes, {sum(len(t.notes) for t in doc.tracks)} notes")
        if a.wav:
            to_wav(doc, a.wav)
            print(f"wrote {a.wav}")
        return 0
    if a.cmd == "import":
        with open(a.file, "rb") as f:
            text, notes = from_midi(f.read(), a.grid)
        with open(a.o, "w", encoding="utf-8") as f:
            f.write(text)
        print("\n".join(notes))
        print(f"wrote {a.o}")
        return 0
    if a.cmd == "cmp":
        x, y = Counter(note_set(a.a)), Counter(note_set(a.b))
        if x == y:
            print(f"same: {sum(x.values())} notes")
            return 0
        only_a, only_b = x - y, y - x
        print(f"differ: {sum(only_a.values())} notes only in {a.a}, {sum(only_b.values())} only in {a.b}")
        for label, c in ((a.a, only_a), (a.b, only_b)):
            for (dr, prog, s, d, p), _ in sorted(c.items(), key=lambda kv: kv[0][2])[:10]:
                print(f"  only in {label}: {'drum ' + str(p) if dr else name_of(p)} at {float(s / PPQ):.3f} quarters, "
                      f"{float(d / PPQ):.3f} long" + ("" if dr else f", program {prog}"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
