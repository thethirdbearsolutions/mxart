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

Commands: check, lint, explain, brief, roll, render, import, cmp. Python 3.9+; --wav needs numpy.
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


# ---------------------------------------------------------------- checking: lint

def sounding(t):
    """cell -> {pitch: attacked?} for a pitched track."""
    m = {}
    for n in t.notes:
        for k in range(n.dur):
            m.setdefault(n.start + k, {})[n.pitch] = k == 0
    return m


def lint(doc, cap=8, harmony=False):
    info, warn, harm = [], [], []
    g, fl = doc.grid, doc.flats
    pitched = [t for t in doc.tracks if t.kind == "track"]
    secs = doc.nbars * g * float(doc.cell_ticks) / PPQ * 60 / doc.tempo
    info.append(f"{doc.path}: {doc.nbars} bars, {doc.num}/{doc.den}, grid {g}, {doc.tempo} bpm, "
                f"{'key ' + doc.key[2] + ' ' + doc.key[1] if doc.key else 'no key'}, {secs:.1f} s")
    for t in doc.tracks:
        if not t.notes:
            warn.append(f"W_EMPTY_TRACK (track {t.name}): no notes")
            continue
        if t.kind == "drums":
            info.append(f"  {t.name:<8} drums       {len(t.notes):>3} hits")
            continue
        ps = [n.pitch for n in t.notes]
        top, cnt = Counter(ps).most_common(1)[0]
        share = cnt / len(ps)
        line = (f"  {t.name:<8} program {t.program:<3} {len(ps):>3} notes  {name_of(min(ps), fl)}..{name_of(max(ps), fl)}  "
                f"most used {name_of(top, fl)} {share:.0%}")
        if share >= 0.5 and len(ps) >= 8:
            warn.append(f"W_MONOTONE (track {t.name}): {cnt} of {len(ps)} notes ({share:.0%}) are {name_of(top, fl)}")
        # melodic leaps: between successive attacks, top note of each
        heads = {}
        for n in t.notes:
            heads[n.start] = max(heads.get(n.start, (0, n))[0], n.pitch), n
        seq = [heads[s] for s in sorted(heads)]
        leaps = [(abs(b[0] - a[0]), a, b) for a, b in zip(seq, seq[1:])]
        if leaps:
            big = max(leaps, key=lambda x: x[0])
            line += f"  largest leap {big[0]}"
            for d, a, b in leaps:
                if d > 12:
                    warn.append(f"W_LEAP (track {t.name}, {doc.where(b[1].start)}): {name_of(a[0], fl)} to "
                                f"{name_of(b[0], fl)} is {d} semitones")
        if doc.key:
            last = max(t.notes, key=lambda n: (n.start, -n.pitch))
            deg = (last.pitch - doc.key[0]) % 12
            line += f"  ends on {name_of(last.pitch, fl)} ({DEGREES.get(deg, 'off key')})"
            offs = [n for n in t.notes if not doc.in_key(n.pitch)]
            for n in offs[:cap]:
                harm.append(f"W_OFF_KEY (track {t.name}, {doc.where(n.start)}): {name_of(n.pitch, fl)} isn't in "
                            f"{doc.key[2]} {doc.key[1]}  [{doc.path}:{n.line}]")
            if cap is not None and len(offs) > cap:
                harm.append(f"W_OFF_KEY (track {t.name}): and {len(offs) - cap} more")
        if t.range:
            for n in t.notes:
                if not t.range[0] <= n.pitch <= t.range[1]:
                    warn.append(f"W_RANGE (track {t.name}, {doc.where(n.start)}): {name_of(n.pitch, fl)} is outside "
                                f"{name_of(t.range[0], fl)}..{name_of(t.range[1], fl)}")
        info.append(line)
        # repeated and transposed bars
        sigs = []
        for b in range(doc.nbars):
            lo, hi = b * g, (b + 1) * g
            sigs.append(tuple(sorted((max(n.start, lo) - lo, min(n.start + n.dur, hi) - max(n.start, lo), n.pitch,
                                      n.start < lo) for n in t.notes if n.start < hi and n.start + n.dur > lo)))
        rep, uniq = [], 0
        for b, s in enumerate(sigs):
            hit = None
            for a in range(b):
                if not s or len(s) != len(sigs[a]):
                    continue
                if s == sigs[a]:
                    hit = f"bar {b + 1} = bar {a + 1}"
                    break
                shifts = {x[2] - y[2] for x, y in zip(s, sigs[a])}
                if len(shifts) == 1 and all(x[:2] + x[3:] == y[:2] + y[3:] for x, y in zip(s, sigs[a])):
                    hit = f"bar {b + 1} = bar {a + 1} {next(iter(shifts)):+d}"
                    break
            uniq += hit is None
            if hit:
                rep.append(hit)
        info.append(f"  {'':<8} {uniq} of {doc.nbars} bars are new material" + (": " + ", ".join(rep) if rep else ""))
        if doc.nbars >= 4 and uniq == 1:
            warn.append(f"W_REPEAT (track {t.name}): every bar repeats or transposes bar 1")
    # semitone clashes, within and across pitched tracks
    snd = {t.name: sounding(t) for t in pitched}
    runs = {}
    for cell in range(doc.nbars * g):
        now = [(p, att, t.name) for t in pitched for p, att in snd[t.name].get(cell, {}).items()]
        for i, (p1, a1, n1) in enumerate(now):
            for p2, a2, n2 in now[i + 1:]:
                if abs(p1 - p2) % 12 in (1, 11):
                    key = tuple(sorted([(n1, p1), (n2, p2)]))
                    r = runs.get(key)
                    if r and r[-1][1] == cell:
                        r[-1][1] = cell + 1
                    else:
                        runs.setdefault(key, []).append([cell, cell + 1, a1 and a2])
    for ((n1, p1), (n2, p2)), rs in sorted(runs.items(), key=lambda kv: kv[1][0][0]):
        for s, e, both in rs:
            kind = "a minor 2nd/9th" if (max(p1, p2) - min(p1, p2)) % 12 == 1 else "a major 7th"
            harm.append(f"W_CLASH ({doc.where(s)}{', on the beat' if doc.on_beat(s) else ''}): {n1} {name_of(p1, fl)} "
                        f"against {n2} {name_of(p2, fl)}, {kind}, for {e - s} cell(s)"
                        + (", both attacked together" if both else ""))
    for b in range(doc.nbars):
        if not any(b * g <= n.start < (b + 1) * g for t in doc.tracks for n in t.notes):
            warn.append(f"W_EMPTY_BAR (bar {b + 1}): no track attacks a note")
    for line, names in doc.voices:
        pw = part_writing(doc, names)
        warn += [w for w in pw if not w.startswith("W_CROSSING")]
        harm += [w for w in pw if w.startswith("W_CROSSING")]
    if harmony:
        warn += harm
    elif harm:
        n = Counter(w.split()[0] for w in harm)
        info.append(f"  not listed: {n['W_OFF_KEY']} line(s) of notes outside the key, {n['W_CLASH']} semitone clash(es), "
                    f"{n['W_CROSSING']} voice crossing(s). Written music is full of all three; lint --harmony lists them")
    return info, sorted(warn, key=lambda w: w.split()[0])


def part_writing(doc, names):
    """Parallel fifths and octaves between the voices of a @voices group, and adjacent voices that cross."""
    fl, out = doc.flats, []
    vs = [next(t for t in doc.tracks if t.name == n) for n in names]
    snd = []
    for t in vs:
        m = {}
        for n in t.notes:
            for k in range(n.dur):
                m[n.start + k] = (n.pitch, n.start)
        snd.append(m)
    held = 2 * doc.grid // doc.num if doc.grid % doc.num == 0 else doc.grid // 2   # two beats
    for a, b in combinations(range(len(vs)), 2):
        run = None
        for c in range(doc.nbars * doc.grid + 1):
            x1, y1 = snd[a].get(c), snd[b].get(c)
            if b == a + 1:
                if x1 and y1 and y1[0] > x1[0]:
                    run = run or [c, x1[0], y1[0]]
                elif run:
                    out.append(f"W_CROSSING ({doc.where(run[0])}): {names[b]} {name_of(run[2], fl)} is above {names[a]} "
                               f"{name_of(run[1], fl)}, for {c - run[0]} cell(s)")
                    run = None
            x0, y0 = snd[a].get(c - 1), snd[b].get(c - 1)
            if not (x0 and y0 and x1 and y1) or x0[0] == x1[0] or y0[0] == y1[0]:
                continue
            i0, i1 = (x0[0] - y0[0]) % 12, (x1[0] - y1[0]) % 12
            if i0 == i1 and i0 in (0, 7) and (x1[0] - x0[0]) * (y1[0] - y0[0]) > 0:
                brk = min(c - x0[1], c - y0[1]) >= held
                out.append(f"{'W_PARALLEL_5TH' if i0 else 'W_PARALLEL_8VE'} ({doc.where(c)}): {names[a]} and {names[b]} move "
                           f"{name_of(x0[0], fl)}/{name_of(y0[0], fl)} to {name_of(x1[0], fl)}/{name_of(y1[0], fl)}"
                           + (", after a held note (fine if that is a phrase break)" if brk else ""))
    return out


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


# ---------------------------------------------------------------- the knowledge base
# Each code is an entry: what it means, where it stands, what was measured, when it is wrong, and
# the sentence that makes a model avoid it. A warning is where a finding lives; `explain` reads it back.
# Rates are from the 2026-11-21 bench: 36 Bach chorales, 146 Corelli trio-sonata movements, Haydn and
# Saint-Georges quartets, Buxtehude, Hummel's op. 67 preludes, 34 Essen folk songs, and model-written tunes.

KB = {
    "W_PARALLEL_5TH": dict(
        what="Two voices a perfect fifth apart both move the same way to another perfect fifth.",
        status="active, only between the voices of a @voices group",
        kinds=("parts",),
        evidence=["Mid-phrase, per 1000 paired moves: Bach chorales 0.7, Corelli 1.4, model chorales 7.2 and 7.4 "
                  "(two independent batches, 26 chorales, 14 with at least one).",
                  "music21's own test agrees on the model chorales (14 against 13 in the second batch).",
                  "Injected into Bach, the lint catches 87 to 91% of them.",
                  "With the remedy sentence in the brief: 0.6 per 1000 (16 chorales), Bach's rate, at no extra cost.",
                  "Repair, 10 chorales: a model fixes them with this warning (18 s), by reading alone (54 s), or with "
                  "its own throwaway checker (41 s). Same result; the warning is faster and confirms the edit landed."],
        exceptions=["After a note held two beats or more it is usually a phrase break, and allowed. Half of one "
                    "batch's raw hits were these; they are marked, not hidden.",
                    "Fifths by contrary motion (one voice jumps an octave to dodge the rule) are not caught. "
                    "music21 catches them; two plain-Python repairs made exactly this move."],
        remedy="Avoid parallel fifths and parallel octaves between voices."),
    "W_PARALLEL_8VE": dict(
        what="Two voices an octave or unison apart both move the same way to another octave or unison.",
        status="active, only between the voices of a @voices group",
        kinds=("parts",),
        evidence=["Mid-phrase, per 1000 paired moves: Bach chorales 0.1, Corelli 0.5.",
                  "Model chorales: 6.5 in the first ten (two agents, five each), 0.0 in sixteen written one per "
                  "agent. A habit of an agent, not of the model."],
        exceptions=["Only a fault in strict part-writing. Instruments double in octaves on purpose: Haydn quartets "
                    "204 per 1000, Saint-Georges 142, Hummel's keyboard preludes 117. Don't put those in @voices."],
        remedy="Avoid parallel fifths and parallel octaves between voices."),
    "W_CLASH": dict(
        what="Two sounding notes a minor 2nd/9th or major 7th apart.",
        status="demoted: listed only by lint --harmony",
        kinds=(),
        evidence=["Per 100 notes: model chorales 0.62, Corelli 2.92, Bach 3.16, Saint-Georges 4.50, Haydn 4.88, "
                  "Buxtehude 5.16, Hummel 8.09. It rises with craft: it counts passing notes and suspensions."],
        exceptions=["Still the quickest way to find one wrong note: with --harmony, a note moved a semitone is "
                    "caught 71% of the time in Bach."],
        remedy=None),
    "W_OFF_KEY": dict(
        what="A note outside the scale of the declared key.",
        status="demoted: listed only by lint --harmony",
        kinds=(),
        evidence=["Per 100 notes: model chorales 1.94, Bach 4.86, Corelli 5.00, Buxtehude 6.37, Hummel 10.46, "
                  "Saint-Georges 11.19, Haydn 12.77. Real music leaves the key; a file has one key line."],
        exceptions=["In a single folk melody it is rare (0.91 per 100 in Essen, 0 in ten model tunes) and worth reading."],
        remedy=None),
    "W_CROSSING": dict(
        what="A lower voice of a @voices group sounds above the voice listed before it.",
        status="demoted: listed only by lint --harmony",
        kinds=(),
        evidence=["Per 100 bars: Bach chorales 10, Corelli 36 (the two violins trade places constantly), "
                  "model chorales 0."],
        exceptions=["With --harmony it catches most notes written an octave out."],
        remedy=None),
    "W_LEAP": dict(
        what="A voice moves more than an octave between two attacks.",
        status="active; the octave threshold is calibrated on sung lines only",
        kinds=("parts", "melody"),
        evidence=["Per 100 notes: Bach chorales 0.02, Essen folk songs 0.11, model tunes 0.",
                  "Instrumental lines leap freely: Corelli 0.68, Haydn 1.42, Hummel 2.37.",
                  "A note written an octave out is caught 63 to 65% of the time."],
        exceptions=["Expect noise on violin, keyboard and bass parts."],
        remedy=None),
    "W_MONOTONE": dict(
        what="Half or more of a track's notes are one pitch (tracks of 8 notes or more).",
        status="active; the 50% threshold is a guess",
        kinds=("parts",),
        evidence=["Fired on no voice of 36 Bach chorales and on 8 voices across 26 model chorales (5 altos, 3 tenors), "
                  "and on 3 more across the 16 written with the parallel-fifths sentence. The sentence below is untried."],
        exceptions=["It is a whole-track measure: two bars stuck on one pitch inside a longer tune go unseen "
                    "(caught 6 to 7% of the time when injected)."],
        remedy="Give the alto and tenor lines of their own; don't park an inner voice on one note."),
    "W_RANGE": dict(what="A note outside the track's declared range=LO..HI.", status="active when a range is declared",
                    kinds=("parts", "melody"), evidence=["No corpus measurement yet."], exceptions=[], remedy=None),
    "W_REPEAT": dict(what="Every bar of a track repeats or transposes bar 1 (4 bars or more).", status="active",
                     kinds=(), evidence=["No corpus measurement yet."], exceptions=["A ground bass is meant to."], remedy=None),
    "W_EMPTY_BAR": dict(what="No track attacks a note anywhere in a bar.", status="active", kinds=(),
                        evidence=["Fired once in 36 Bach chorales and once in 34 folk songs. A bar deleted from every "
                                  "voice is caught every time."],
                        exceptions=["A held final chord across a bar line trips it."], remedy=None),
    "W_EMPTY_TRACK": dict(what="A track with no notes.", status="active", kinds=(), evidence=["No corpus measurement yet."],
                          exceptions=[], remedy=None),
    "N_ON_THE_BEAT": dict(
        what="Finding with no check yet: the model writes block chords on the beat.",
        status="no check; describe your tune against a reference to see it",
        kinds=("parts",),
        evidence=["Attacks off the beat, median per voice: model chorales 1 to 3%, Bach 20%, Corelli 32%, Haydn 42%, "
                  "Buxtehude 52%. Bars with a rhythm not heard before: model 38%, Bach 69%.",
                  "The parallel-fifths sentence did not move it (3.4% with and without).",
                  "Model folk melodies are closer: 20% off the beat against 34% in Essen."],
        exceptions=["Not a fault. A hymn in plain block chords is a legitimate thing to want."],
        remedy="Let the lower voices move between the beats with passing notes and suspensions, as Bach's do."),
    "N_LATE_VOICE": dict(
        what="Finding with no check yet: one voice starts bars after the others because of a stray timing event.",
        status="no check",
        kinds=("parts",),
        evidence=["One of 42 model chorales had its soprano enter nine bars late (a tempo event with a delay, written "
                  "before the first note). The lint was silent; of 30 repair agents shown that piece, one noticed."],
        exceptions=["Fugues and rounds stagger entries on purpose."],
        remedy=None),
    "N_GRID": dict(
        what="Finding about the format: grid counts cells per bar, so its meaning changes with the metre.",
        status="format wart",
        kinds=(),
        evidence=["Importing 3/4 pieces at grid 16 moved 4% of Bach's notes; grid 12 moved none.",
                  "At a sixteenth-note grid, notes that don't fit: Bach 0%, Corelli 0.3%, Saint-Georges 5%, Buxtehude 6%, "
                  "Haydn quartets 11.5%, Hummel 24% (triplets, faster notes, ornaments)."],
        exceptions=[], remedy=None),
}


def explain(code=None):
    if code is None:
        return "\n".join(f"{k:<16} {v['status']}" for k, v in KB.items())
    e = KB.get(code.upper())
    if e is None:
        return None
    out = [f"{code.upper()}: {e['what']}", f"  status: {e['status']}"]
    for title, key in (("measured", "evidence"), ("when it is wrong", "exceptions")):
        if e[key]:
            out.append(f"  {title}:")
            out += [f"    - {x}" for x in e[key]]
    out.append(f"  say this in the brief: {e['remedy']}" if e["remedy"] else "  no sentence for the brief yet")
    return "\n".join(out)


def brief(kind):
    seen = []
    for e in KB.values():
        if e["remedy"] and kind in e["kinds"] and e["remedy"] not in seen:
            seen.append(e["remedy"])
    return seen


# ---------------------------------------------------------------- commands

def main(argv=None):
    ap = argparse.ArgumentParser(prog="mxart", description="Music as text: check it, look at it, lint it, render it.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check", help="format errors, each with a code and a location; exit 1 on any")
    p.add_argument("files", nargs="+")
    p = sub.add_parser("lint", help="what a listener would notice, as numbers and located warnings")
    p.add_argument("file"); p.add_argument("--strict", action="store_true", help="exit 1 on any warning")
    p.add_argument("--harmony", action="store_true", help="also list notes outside the key, semitone clashes and voice crossings")
    p = sub.add_parser("roll", help="a text piano roll with bar and beat rulers")
    p.add_argument("file"); p.add_argument("--bars", type=int, default=4, help="bars per line (default 4)")
    p.add_argument("--full", action="store_true", help="a row for every semitone, not only the pitches used")
    p = sub.add_parser("render", help="write a .mid (and --wav, a plain synth, to listen)")
    p.add_argument("file"); p.add_argument("-o", required=True); p.add_argument("--wav")
    p = sub.add_parser("import", help="a .mid as .mx text, quantized to --grid")
    p.add_argument("file"); p.add_argument("-o", required=True); p.add_argument("--grid", type=int, default=16)
    p = sub.add_parser("explain", help="what a code means, what was measured, when it is wrong, what to say instead")
    p.add_argument("code", nargs="?")
    p = sub.add_parser("brief", help="the sentences to put in a composing brief, from the knowledge base")
    p.add_argument("--kind", choices=("parts", "melody"), default="parts", help="parts: several voices; melody: one line")
    p = sub.add_parser("cmp", help="do two files (.mx or .mid) hold the same notes? velocities aren't compared")
    p.add_argument("a"); p.add_argument("b")
    a = ap.parse_args(argv)

    if a.cmd == "explain":
        text = explain(a.code)
        print(text if text else f"explain: E_BAD_ARG: no entry for '{a.code}'; codes: {' '.join(KB)}")
        return 0 if text else 1
    if a.cmd == "brief":
        print("\n".join(brief(a.kind)))
        return 0
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
    if a.cmd == "lint":
        info, warn = lint(load_ok(a.file), harmony=a.harmony)
        print("\n".join(info))
        print("\n".join(warn) if warn else "no warnings")
        if warn:
            print(f"{len(warn)} warning(s)")
        return 1 if warn and a.strict else 0
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
