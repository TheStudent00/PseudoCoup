"""
track.py — the MEASURED progress dashboard (the anti-drift instrument).

Two actions, both from one source of truth (PROGRESS_history.json + PROGRESS_ondeck.md):

  measure   re-run the gates/gauges, append a dated sample to PROGRESS_history.json
  render    regenerate PROGRESS.html (SVG trend charts) and PROGRESS.md (ascii sparklines)
  (default) measure, then render

The numbers are MEASURED here, never hand-typed. A gate that goes red, or a count that drops, shows up
as a red chip or a dipping line on the next run — that is the whole point: the board cannot claim "done"
while a gate disagrees. Run from anywhere:  python3 tools/pseudokotlin/track.py

What each metric reads, and the gauge it runs:
  parse     measure.py        files that transpile + py_compile clean   (ratio, up)
  load      loadcheck.py      non-UI domain modules that import clean    (ratio, up)
  logic     oracle.py --all   engine methods whose result matches Kotlin (ratio, up)
  data      datalayer_oracle  instrumented DAO/txn test classes green    (ratio, up)
  extern    externals.py      external names USED but unwrapped          (count, down=better)
  unrouted  coverage.py       grammar kinds with no handler (the worklist)(count, down=better)
"""
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # tools/pseudokotlin -> PseudoCoup
HIST = os.path.join(ROOT, "PROGRESS_history.json")
ONDECK = os.path.join(ROOT, "PROGRESS_ondeck.md")
HTML = os.path.join(ROOT, "PROGRESS.html")
MD = os.path.join(ROOT, "PROGRESS.md")

# key -> (label, goal, kind). goal "up": more is better; "down": fewer is better (a remaining-work count).
METRICS = [
    ("parse",    "Parse — all .kt transpile + compile",  "up",   "ratio"),
    ("load",     "Load — non-UI domain imports clean",   "up",   "ratio"),
    ("logic",    "Logic — engine methods match Kotlin",  "up",   "ratio"),
    ("data",     "Data — instrumented DB tests green",   "up",   "ratio"),
    ("extern",   "External gaps — used but unwrapped",   "down", "count"),
    ("unrouted", "Grammar kinds unrouted — the worklist","down", "count"),
]
GATES = ["parse", "load", "extern", "logic", "data"]
# the instrumented suite the data gate draws from. 2 run green; 2 are blocked ABOVE the data layer
# (BackupRepositoryRoundTripTest, MigrationTest) — see PROGRESS_ondeck.md. Bump when one starts running.
TOTAL_INSTRUMENTED = 4


# ---- measure: run the gauges, parse their summary lines (fail loud if a format moved) ------------ #
def _run(script, *args):
    r = subprocess.run([sys.executable, script, *args], cwd=HERE,
                       capture_output=True, text=True, timeout=600)
    return r.stdout + r.stderr


def _grab(pattern, text, what):
    m = re.search(pattern, text)
    if m is None:
        raise SystemExit(f"track.py: could not read {what} — the gauge's summary line moved.\n"
                         f"  pattern: {pattern!r}")
    return m


def measure():
    parse = _grab(r"ALL:\s*(\d+)/(\d+)\s*compile-clean", _run("measure.py"), "parse count")
    load = _grab(r"load clean\s*:\s*(\d+)\s*/\s*(\d+)", _run("loadcheck.py"), "load count")
    extern = _grab(r"unwrapped:\s*(\d+)", _run("externals.py"), "external gaps")
    cover = _grab(r"UNROUTED\s*\((\d+)\)", _run("coverage.py"), "unrouted count")

    orc = _run("oracle.py", "--all")
    meth = re.findall(r"python:\s*(\d+)/(\d+)\s*methods", orc)
    if not meth:
        raise SystemExit("track.py: could not read oracle method counts.")
    logic_n = sum(int(a) for a, _ in meth)
    logic_d = sum(int(b) for _, b in meth)
    logic_gate = "ALL GREEN" in orc

    dl = _run("datalayer_oracle.py")
    data_green = len(re.findall(r"^===\s+\w+\s+\(\d+/\d+\)", dl, re.M))
    data_gate = "ALL GREEN" in dl

    pn, pd = int(parse.group(1)), int(parse.group(2))
    ln, ld = int(load.group(1)), int(load.group(2))
    ex = int(extern.group(1))
    un = int(cover.group(1))
    return {
        "date": datetime.date.today().isoformat(),
        "parse": [pn, pd], "load": [ln, ld], "logic": [logic_n, logic_d],
        "data": [data_green, TOTAL_INSTRUMENTED], "extern": ex, "unrouted": un,
        "gates": {"parse": pn == pd, "load": ln == ld, "extern": ex == 0,
                  "logic": logic_gate, "data": data_gate},
    }


def append_sample(hist, sample):
    samples = hist.setdefault("samples", [])
    if samples and samples[-1]["date"] == sample["date"]:
        samples[-1] = sample                             # idempotent: one sample per day, latest wins
    else:
        samples.append(sample)
    return hist


# ---- shared helpers -------------------------------------------------------------------------------- #
def _val(sample, key):
    """the plotted value for a metric in a sample (the numerator for a ratio, the count otherwise)."""
    v = sample.get(key)
    return v[0] if isinstance(v, list) else v


def _ceiling(sample, key, kind):
    return sample.get(key, [0, 0])[1] if kind == "ratio" else None


def _fmt(sample, key, kind):
    v = sample.get(key)
    if kind == "ratio":
        return f"{v[0]}/{v[1]}"
    return str(v)


def _spark(values):
    blocks = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    if hi == lo:
        return blocks[3] * len(values)
    return "".join(blocks[round((v - lo) / (hi - lo) * (len(blocks) - 1))] for v in values)


def load_history():
    with open(HIST) as f:
        return json.load(f)


def read_ondeck():
    if not os.path.exists(ONDECK):
        return []
    items = []
    for line in open(ONDECK):
        m = re.match(r"\s*-\s*\[([^\]]+)\]\s*(.+?)\s*(?:—|--)\s*(.+)", line)
        if m:
            items.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
        elif re.match(r"\s*-\s+\S", line):              # a plain "- task" with no [area]/— detail
            items.append(("", line.strip()[2:].strip(), ""))
    return items


# ---- render: HTML (SVG charts) --------------------------------------------------------------------- #
def _chart_svg(key, label, goal, kind, samples):
    W, H, padx, padtop, padbot = 250, 96, 8, 22, 16
    pts = [(s["date"], _val(s, key)) for s in samples]
    vals = [v for _, v in pts]
    ceil = _ceiling(samples[-1], key, kind)
    top = max([*(vals or [0]), ceil or 0, 1])
    iw, ih = W - 2 * padx, H - padtop - padbot

    def xy(i, v):
        x = padx + (iw if len(pts) == 1 else iw * i / (len(pts) - 1))
        y = padtop + ih - (ih * v / top)
        return x, y

    cur = vals[-1]
    green = (kind == "ratio" and ceil and cur == ceil) or (goal == "down" and cur == 0)
    stroke = "#5fd08a" if green else "#e0b15f"
    body = []
    if kind == "ratio" and ceil:                         # faint ceiling (the denominator) line
        cy = padtop + ih - (ih * ceil / top)
        body.append(f'<line x1="{padx}" y1="{cy:.1f}" x2="{padx+iw}" y2="{cy:.1f}" '
                    f'stroke="#2f3b63" stroke-dasharray="3 3"/>')
    if len(pts) > 1:
        poly = " ".join(f"{x:.1f},{y:.1f}" for i, (x, y) in
                        enumerate(xy(i, v) for i, v in enumerate(vals)))
        body.append(f'<polyline fill="none" stroke="{stroke}" stroke-width="2" points="{poly}"/>')
    for i, v in enumerate(vals):
        x, y = xy(i, v)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="{stroke}"/>')
    lx, ly = xy(len(vals) - 1, cur)
    arrow = " ↓" if goal == "down" else ""
    body.append(f'<text x="{padx+iw}" y="14" text-anchor="end" fill="{stroke}" '
                f'font-size="15" font-weight="700">{_fmt(samples[-1], key, kind)}{arrow}</text>')
    body.append(f'<text x="{padx}" y="14" fill="#9aa6c4" font-size="11">{label}</text>')
    return (f'<svg width="100%" viewBox="0 0 {W} {H}" preserveAspectRatio="none" '
            f'style="display:block">{"".join(body)}</svg>')


def render_html(hist, ondeck):
    samples = hist["samples"]
    last = samples[-1]
    chips = []
    for g in GATES:
        ok = last["gates"].get(g, False)
        chips.append(f'<span class="chip {"ok" if ok else "bad"}">{g} '
                     f'{"✓" if ok else "✗"}</span>')
    charts = "".join(f'<div class="card">{_chart_svg(k, lbl, goal, kind, samples)}</div>'
                     for k, lbl, goal, kind in METRICS)
    miles = "".join(f'<li><span class="date">{m["date"]}</span> {m["text"]}</li>'
                    for m in reversed(hist.get("milestones", [])))
    deck = []
    for i, (area, task, detail) in enumerate(ondeck):
        tag = f'<span class="area">{area}</span> ' if area else ""
        nx = ' <span class="next">next</span>' if i == 0 else ""
        d = f'<div class="det">{detail}</div>' if detail else ""
        deck.append(f"<li>{tag}{task}{nx}{d}</li>")
    deck_html = "<ol>" + "".join(deck) + "</ol>" if deck else "<p class='mut'>(empty)</p>"
    return _HTML.format(date=hist.get("generated", last["date"]), chips="".join(chips),
                        charts=charts, milestones=miles, ondeck=deck_html)


# ---- render: Markdown (ascii sparklines, git-diff friendly) --------------------------------------- #
def render_md(hist, ondeck):
    samples = hist["samples"]
    last = samples[-1]
    rows = ["| metric | now | trend | gate |", "|---|---|---|---|"]
    for k, lbl, goal, kind in METRICS:
        series = [_val(s, k) for s in samples]
        gate = ""
        if k in last["gates"]:
            gate = "🟢" if last["gates"][k] else "🔴"
        arrow = " ↓better" if goal == "down" else ""
        rows.append(f"| {lbl} | **{_fmt(last, k, kind)}**{arrow} | `{_spark(series)}` | {gate} |")
    deck = []
    for i, (area, task, detail) in enumerate(ondeck):
        tag = f"**[{area}]** " if area else ""
        nx = "  ← next" if i == 0 else ""
        det = f"\n  - {detail}" if detail else ""
        deck.append(f"1. {tag}{task}{nx}{det}")
    miles = "\n".join(f"- `{m['date']}` {m['text']}" for m in reversed(hist.get("milestones", [])))
    return _MD.format(date=hist.get("generated", last["date"]),
                      table="\n".join(rows), ondeck="\n".join(deck) or "_(empty)_",
                      milestones=miles)


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action in ("measure", "all"):
        hist = load_history()
        hist["generated"] = datetime.date.today().isoformat()
        append_sample(hist, measure())
        with open(HIST, "w") as f:
            json.dump(hist, f, indent=2)
        print(f"measured -> {os.path.relpath(HIST, ROOT)} ({len(hist['samples'])} samples)")
    if action in ("render", "all"):
        hist = load_history()
        ondeck = read_ondeck()
        with open(HTML, "w") as f:
            f.write(render_html(hist, ondeck))
        with open(MD, "w") as f:
            f.write(render_md(hist, ondeck))
        print(f"rendered -> PROGRESS.html + PROGRESS.md  (as of {hist.get('generated')})")


_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WFL → Python — progress</title>
<style>
  body{{margin:0 auto;max-width:1000px;background:#0f1320;color:#e8ecf7;padding:32px 28px 80px;
    font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
  h1{{font-size:23px;margin:0 0 4px}}
  h2{{font-size:13px;text-transform:uppercase;letter-spacing:1.5px;color:#9aa6c4;margin:34px 0 12px}}
  .sub{{color:#9aa6c4;font-size:13px;margin:0 0 4px}}
  .mut{{color:#9aa6c4}}
  code{{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;background:#222a45;padding:1px 6px;
    border-radius:5px;color:#cdd7f5}}
  .panel{{background:#171c2e;border:1px solid #2a3354;border-radius:12px;padding:16px 18px}}
  .chips{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 4px}}
  .chip{{font-size:13px;font-weight:600;padding:4px 11px;border-radius:7px}}
  .chip.ok{{background:#16331f;color:#7fe0a3;border:1px solid #2f5d45}}
  .chip.bad{{background:#371a1a;color:#e88;border:1px solid #6d3030}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
  .card{{background:#141a2c;border:1px solid #2a3354;border-radius:10px;padding:8px 6px 2px}}
  ol,ul{{margin:6px 0 0;padding-left:22px}} li{{margin:7px 0}}
  .area{{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#0f1320;background:#7f93c4;
    padding:1px 6px;border-radius:5px;font-weight:700}}
  .next{{font-size:11px;color:#0f1320;background:#5fd08a;padding:1px 6px;border-radius:5px;font-weight:700}}
  .det{{color:#9aa6c4;font-size:13px;margin-top:2px}}
  .tl{{list-style:none;padding-left:0}} .tl li{{margin:4px 0}}
  .date{{display:inline-block;min-width:84px;color:#7f93c4;font-family:ui-monospace,monospace;font-size:12px}}
</style></head><body>

<h1>WFL → Python — progress</h1>
<p class="sub">Measured by re-running the gates (<code>tools/pseudokotlin/track.py</code>). A red chip or a
dipping line is a real regression — the board can't claim done while a gate disagrees.</p>
<p class="sub mut">As of {date}. Reload after a <code>track.py</code> run to refresh.</p>

<h2>Gates — pass / fail right now</h2>
<div class="chips">{chips}</div>

<h2>Momentum — each metric over time</h2>
<div class="grid">{charts}</div>

<h2>On-deck — next sub-tasks (top = next)</h2>
<div class="panel">{ondeck}</div>

<h2>Milestones — what landed, when</h2>
<div class="panel"><ul class="tl">{milestones}</ul></div>

<h2 class="mut">Orientation</h2>
<div class="panel mut" style="font-size:13px">
The <b>foundation</b> is the 1:1 Python <b>KtToPy</b> produces from the Kotlin copy
(<code>WFL_MixingCenter/*.py</code>). The one goal now: complete the transpiler so the foundation is solid.
Pipeline: parse → resolve (classify every name) → map (wrap externals by origin) → generate (code + imports).
Detail and narrative live in <code>DevComms/</code> logs; this page is the dashboard.
</div>

</body></html>
"""

_MD = """# WFL → Python — progress

Measured by re-running the gates (`tools/pseudokotlin/track.py`) — never hand-typed. A 🔴 gate or a falling
sparkline is a real regression, not a stale doc. (Browser version with trend charts: `PROGRESS.html`.)

As of {date}.

## Gates + momentum

{table}

## On-deck — next sub-tasks (top = next)

{ondeck}

## Milestones — what landed, when

{milestones}

## Orientation

The **foundation** is the 1:1 Python **KtToPy** produces from the Kotlin copy (`WFL_MixingCenter/*.py`); the
one goal now is to complete the transpiler so it is solid. Pipeline: parse → resolve (classify every name) →
map (wrap externals by origin) → generate (code + imports). Narrative detail lives in `DevComms/` logs.
"""


if __name__ == "__main__":
    main()
