"""
html_generator.py - Generates an interactive HTML report visualizing NFAs and DFAs.

For every case the report shows the original NFA and the equivalent DFA: summary chips,
a diagram (layered left-to-right layout, double rings for final states, arrow for initial
states) and a transition table.
"""
import json
from typing import Dict, Iterable, List, Tuple

from models import NFA, DFA


def _fmt_set(values: Iterable[int]) -> str:
    """{1, 5} style, used in tables and chips."""
    ordered = sorted(values)
    return "{" + ", ".join(map(str, ordered)) + "}" if ordered else "∅"


def _compact_set(values: Iterable[int]) -> str:
    """{1,5} style (no blanks), used as caption under the DFA states in the diagram."""
    ordered = sorted(values)
    return "{" + ",".join(map(str, ordered)) + "}" if ordered else "∅"


def _merge_edges(raw_edges: List[Tuple[int, int, str]]) -> List[Dict]:
    """One edge per (source, target) pair, labelled with ALL its symbols ("a, b")."""
    merged: Dict[Tuple[int, int], List[str]] = {}
    for src, dst, sym in raw_edges:
        symbols = merged.setdefault((src, dst), [])
        if sym not in symbols:
            symbols.append(sym)
    return [
        {"from": src, "to": dst, "label": ", ".join(symbols)}
        for (src, dst), symbols in merged.items()
    ]


class HTMLReportGenerator:
    @staticmethod
    def _nfa_data(nfa: NFA) -> Dict:
        nodes, raw_edges, table = [], [], []

        for i in range(1, nfa.num_states + 1):
            is_init = i in nfa.initial_states
            is_fin = i in nfa.final_states
            nodes.append({"id": i, "label": str(i), "initial": is_init, "final": is_fin})
            table.append({
                "id": i,
                "is_start": is_init,
                "is_final": is_fin,
                "transitions": {sym: _fmt_set(nfa.get_transition(i, sym)) for sym in nfa.alphabet},
            })

        for src in sorted(nfa.delta):
            for sym in nfa.alphabet:
                for tgt in sorted(nfa.delta[src].get(sym, set())):
                    raw_edges.append((src, tgt, sym))

        return {
            "graph": {"nodes": nodes, "edges": _merge_edges(raw_edges)},
            "table": table,
            "num_states": nfa.num_states,
            "initial": sorted(nfa.initial_states),
            "final": sorted(nfa.final_states),
        }

    @staticmethod
    def _dfa_data(dfa: DFA) -> Dict:
        nodes, raw_edges, table = [], [], []

        for st_id, st_set in enumerate(dfa.states, 1):
            is_init = st_id == dfa.start_state_id
            is_fin = st_id in dfa.final_state_ids
            nodes.append({
                "id": st_id,
                "label": str(st_id),
                "caption": _compact_set(st_set),
                "initial": is_init,
                "final": is_fin,
                "dead": not st_set,
            })
            table.append({
                "id": st_id,
                "subset": _fmt_set(st_set),
                "is_start": is_init,
                "is_final": is_fin,
                "transitions": dfa.delta.get(st_id, {}),
            })

        for src_id in sorted(dfa.delta):
            for sym in dfa.alphabet:
                if sym in dfa.delta[src_id]:
                    raw_edges.append((src_id, dfa.delta[src_id][sym], sym))

        return {
            "graph": {"nodes": nodes, "edges": _merge_edges(raw_edges)},
            "table": table,
            "initial": dfa.start_state_id,
            "final": list(dfa.final_state_ids),
        }

    @staticmethod
    def generate_html(cases: List[Tuple[NFA, DFA]], filename: str = "resultado_automata.html"):
        cases_data = []
        for case_idx, (nfa, dfa) in enumerate(cases, 1):
            cases_data.append({
                "case_idx": case_idx,
                "alphabet": dfa.alphabet,
                "nfa": HTMLReportGenerator._nfa_data(nfa),
                "dfa": HTMLReportGenerator._dfa_data(dfa),
            })

        # "</" is escaped so the data can never close the <script> tag
        cases_json = json.dumps(cases_data, ensure_ascii=False).replace("</", "<\\/")
        html_content = _HTML_TEMPLATE.replace("__CASES_DATA__", cases_json)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)


# Raw string: the HTML/CSS/JS below is copied as is (backslashes included).
_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Subset Construction - Interactive Visualization</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Outfit:wght@200;300;400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/@viz-js/viz@3.11.0/lib/viz-standalone.js"></script>
<script>window.Viz || document.write('<script src="https://unpkg.com/@viz-js/viz@3.11.0/lib/viz-standalone.js"><\/script>')</script>
<style>
:root{
  --bg-0:#0b0848; --bg-1:#15107a;
  --lav:#c7c6ff; --lav-2:#a5a3f7; --mint:#bdf2d0; --peach:#ffd9c7; --butter:#fff0b8; --sky:#bfe3ff;
  --ink:#eceaff; --muted:#a9a7e6; --line:rgba(199,198,255,.16);
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; min-height:100vh; overflow-x:hidden;
  font-family:'Outfit','Segoe UI',system-ui,-apple-system,sans-serif; font-weight:300;
  color:var(--ink);
  background:#15107a linear-gradient(180deg,#0b0848 0,#15107a 560px);
}
.stars{
  position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.8;
  background-image:
    radial-gradient(1.4px 1.4px at 6% 12%,#fff,transparent 60%),
    radial-gradient(1px 1px at 14% 46%,#dcdcff,transparent 60%),
    radial-gradient(1.2px 1.2px at 23% 8%,#fff,transparent 60%),
    radial-gradient(1px 1px at 31% 71%,#c7c6ff,transparent 60%),
    radial-gradient(1.4px 1.4px at 42% 27%,#fff,transparent 60%),
    radial-gradient(1px 1px at 55% 88%,#dcdcff,transparent 60%),
    radial-gradient(1.2px 1.2px at 63% 15%,#fff,transparent 60%),
    radial-gradient(1px 1px at 71% 58%,#c7c6ff,transparent 60%),
    radial-gradient(1.4px 1.4px at 79% 33%,#fff,transparent 60%),
    radial-gradient(1px 1px at 88% 79%,#dcdcff,transparent 60%),
    radial-gradient(1.2px 1.2px at 94% 21%,#fff,transparent 60%),
    radial-gradient(1px 1px at 97% 64%,#c7c6ff,transparent 60%),
    radial-gradient(1px 1px at 48% 52%,#fff,transparent 60%),
    radial-gradient(1px 1px at 8% 84%,#fff,transparent 60%);
}
.wrap{position:relative; z-index:1; max-width:1240px; margin:0 auto; padding:0 24px}

/* ---------- nav ---------- */
.nav{
  position:sticky; top:16px; z-index:20; max-width:980px; margin:16px auto 0;
  display:flex; align-items:center; justify-content:space-between; gap:16px;
  padding:10px 14px 10px 22px; border-radius:16px;
  background:rgba(32,27,150,.62); border:1px solid var(--line);
  -webkit-backdrop-filter:blur(12px); backdrop-filter:blur(12px);
  font-size:13px; font-weight:400;
}
.nav a{color:var(--lav); text-decoration:none}
.nav a:hover{color:#fff}
.nav-links{display:flex; gap:22px; flex:1}
.nav-links.right{justify-content:flex-end; align-items:center}
.brand{display:flex; align-items:center; gap:9px; color:#fff !important; font-weight:600; font-size:15px; letter-spacing:.01em}
.brand b{font-weight:600; color:var(--mint)}
.btn-dark{background:#05041f; color:#fff !important; padding:8px 16px; border-radius:10px; font-weight:500; white-space:nowrap}
@media (max-width:720px){ .nav-links a.hide-sm{display:none} .nav{margin:16px 12px 0} }

/* ---------- hero ---------- */
.hero{position:relative; z-index:1; text-align:center; padding:84px 20px 0}
.hero h1{
  margin:0 auto; max-width:820px; color:#fff; font-weight:200;
  font-size:clamp(2.1rem,5.2vw,3.6rem); line-height:1.12; letter-spacing:-.01em;
}
.hero h1 em{font-style:normal; color:var(--mint); font-weight:300}
.hero .sub{margin:18px auto 0; font-size:15px; color:var(--muted); max-width:560px; font-weight:300}
.btn{
  display:inline-block; margin-top:26px; padding:11px 22px; border-radius:10px;
  background:#c5f3d2; color:#0d2e1f; font-weight:500; font-size:13px; text-decoration:none;
  box-shadow:0 8px 24px rgba(120,240,170,.18); transition:transform .15s ease, box-shadow .15s ease;
}
.btn:hover{transform:translateY(-2px); box-shadow:0 12px 30px rgba(120,240,170,.28)}
.hero-art{position:relative; height:440px; margin:8px -20px 0}
.hero-art svg{position:absolute; inset:0; width:100%; height:100%}
.hero-art::after{
  content:''; position:absolute; left:0; right:0; bottom:0; height:130px;
  background:linear-gradient(180deg,rgba(21,16,122,0),#15107a);
}

/* ---------- sections ---------- */
section.block{padding:70px 0 0}
.about{max-width:680px; margin:0 auto; text-align:center; font-size:15px; line-height:1.8; color:#d5d4ff}
.about b{color:#fff; font-weight:500}
.about code{font-family:var(--mono); font-size:13px; color:var(--mint)}
h2.title{margin:0 0 26px; color:#fff; font-weight:200; font-size:clamp(1.6rem,3vw,2.2rem)}
.features{display:grid; grid-template-columns:repeat(4,1fr); gap:24px}
.feature .ico{
  width:42px; height:42px; border-radius:11px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#3b36d6,#6b67f6); box-shadow:0 8px 20px rgba(60,54,214,.4);
}
.feature h4{margin:14px 0 4px; color:#fff; font-weight:400; font-size:17px}
.feature p{margin:0; font-size:12.5px; color:var(--muted)}
@media (max-width:820px){ .features{grid-template-columns:repeat(2,1fr)} }

.legend{
  display:flex; flex-wrap:wrap; gap:14px 30px; align-items:center; justify-content:center;
  padding:18px 24px; font-size:13px; color:#d5d4ff;
}
.legend span.item{display:inline-flex; align-items:center; gap:10px}

/* ---------- cards ---------- */
.card{
  background:rgba(255,255,255,.045); border:1px solid var(--line); border-radius:26px; padding:28px;
  -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);
  box-shadow:0 24px 60px rgba(4,3,40,.35);
}
.cases{display:flex; flex-direction:column; gap:36px}
.case-head{display:flex; flex-wrap:wrap; align-items:center; gap:14px 22px; padding-bottom:20px; border-bottom:1px solid var(--line); margin-bottom:22px}
.case-title{margin:0; color:#fff; font-weight:300; font-size:28px}
.case-title small{color:var(--mint); font-size:14px; font-weight:400; margin-left:8px}
.chip-groups{display:flex; flex-direction:column; gap:8px; margin-left:auto}
.chips{display:flex; flex-wrap:wrap; gap:8px}
.chip{
  font-size:12.5px; padding:5px 12px; border-radius:999px; color:#e4e3ff;
  background:rgba(165,163,247,.14); border:1px solid rgba(165,163,247,.32);
}
.chip strong{font-weight:500; color:var(--lav); margin-right:4px}
.chip.mint{background:rgba(189,242,208,.12); border-color:rgba(189,242,208,.35)}
.chip.mint strong{color:var(--mint)}

.panels{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.3fr); gap:22px}
.panel.wide{grid-column:1 / -1}
.panel.wide .canvas{height:600px}
.panels > *, .tables > *{min-width:0}
@media (max-width:1020px){ .panels, .tables{grid-template-columns:1fr} .chip-groups{margin-left:0} .zoom .expand{display:none} }
.panel-head{display:flex; align-items:center; gap:10px; margin-bottom:12px}
.badge{font-size:11px; font-weight:600; letter-spacing:.06em; padding:4px 9px; border-radius:7px; color:#0e0b59}
.badge.nfa{background:var(--sky)}
.badge.dfa{background:var(--lav)}
.panel-head h3{margin:0; color:#fff; font-weight:400; font-size:16px}
.zoom{margin-left:auto; display:flex; gap:6px}
.zoom button{
  width:28px; height:28px; border-radius:8px; border:1px solid var(--line); cursor:pointer;
  background:rgba(255,255,255,.06); color:var(--lav); font-size:15px; line-height:1;
}
.zoom button:hover{background:rgba(255,255,255,.14); color:#fff}
.canvas{
  height:470px; border-radius:16px; overflow:hidden; cursor:grab; position:relative;
  border:1px solid var(--line); background-color:rgba(8,6,60,.5);
  background-image:radial-gradient(rgba(199,198,255,.17) 1px,transparent 1px); background-size:22px 22px;
}
.canvas:active{cursor:grabbing}
.canvas .msg{padding:22px; font-size:13px; color:var(--muted)}
.canvas .msg.err{color:var(--peach)}
.hint{margin:8px 2px 0; font-size:11.5px; color:var(--muted)}

.tables{display:grid; grid-template-columns:1fr 1fr; gap:22px; margin-top:26px}
.tables h3{margin:0 0 12px; color:#fff; font-weight:400; font-size:16px}
.tbl-wrap{overflow-x:auto; border:1px solid var(--line); border-radius:14px}
table{width:100%; border-collapse:collapse; font-family:var(--mono); font-size:13px}
.sym{text-transform:none}
th{
  background:rgba(199,198,255,.12); color:var(--lav); font-weight:700; font-size:11px;
  text-transform:uppercase; letter-spacing:.07em; padding:11px 12px; text-align:center; white-space:nowrap;
}
td{padding:10px 12px; border-top:1px solid var(--line); text-align:center; color:#e6e5ff; font-weight:500; white-space:nowrap}
tbody tr:hover td{background:rgba(255,255,255,.05)}
td.state{font-weight:700; color:#fff}
.tag{display:inline-block; margin-left:8px; padding:1px 8px; border-radius:999px; font-family:'Outfit',sans-serif; font-size:10.5px; font-weight:600; letter-spacing:.03em}
.tag.start{background:var(--lav); color:#1d1a78}
.tag.final{background:var(--mint); color:#0d4a30}
.tag.both{background:var(--butter); color:#5b4400}

footer{position:relative; z-index:1; text-align:center; padding:60px 20px 40px; font-size:12.5px; color:var(--muted)}
footer b{color:var(--lav); font-weight:500}
</style>
</head>
<body>
<div class="stars"></div>

<nav class="nav">
  <div class="nav-links">
    <a href="#overview" class="hide-sm">Overview</a>
    <a href="#legend" class="hide-sm">Legend</a>
  </div>
  <a class="brand" href="#top">
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><circle cx="13" cy="13" r="11.5" fill="none" stroke="#bdf2d0" stroke-width="1.6"/><circle cx="13" cy="13" r="7" fill="#bdf2d0"/></svg>
    <span>Subset<b>Construction</b></span>
  </a>
  <div class="nav-links right">
    <a href="#cases" class="btn-dark">View cases</a>
  </div>
</nav>

<header class="hero" id="top">
  <h1>From <em>non-deterministic</em> to deterministic automata</h1>
  <p class="sub">Interactive visualization of the subset construction (Kozen, Lecture 6). SI2002 Formal Languages.</p>
  <a class="btn" href="#cases">View results</a>

  <div class="hero-art" aria-hidden="true">
    <svg viewBox="0 0 1200 440" preserveAspectRatio="xMidYMax slice">
      <defs>
        <radialGradient id="planet" cx="35%" cy="30%" r="80%">
          <stop offset="0" stop-color="#2d2cb0"/><stop offset=".5" stop-color="#15137f"/><stop offset="1" stop-color="#07053a"/>
        </radialGradient>
        <linearGradient id="ring" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stop-color="#6fb2ff" stop-opacity="0"/><stop offset=".5" stop-color="#9cc9ff"/><stop offset="1" stop-color="#6fb2ff" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="mtnA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d7af4"/><stop offset="1" stop-color="#3b36c6"/></linearGradient>
        <linearGradient id="mtnB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a45d2"/><stop offset="1" stop-color="#2a25a8"/></linearGradient>
      </defs>
      <!-- sparkles -->
      <g fill="#fff">
        <path d="M70 70 Q70 70 76 56 Q82 70 96 76 Q82 82 76 96 Q70 82 56 76 Q70 70 70 70Z" opacity=".95"/>
        <path d="M1130 250 Q1130 250 1134 240 Q1138 250 1148 254 Q1138 258 1134 268 Q1130 258 1120 254 Q1130 250 1130 250Z" opacity=".9"/>
        <circle cx="200" cy="40" r="1.6"/><circle cx="520" cy="60" r="1.3"/><circle cx="760" cy="30" r="1.6"/><circle cx="1010" cy="70" r="1.3"/><circle cx="360" cy="110" r="1.2"/>
      </g>
      <!-- ring (back) + planet + ring (front) -->
      <g transform="rotate(-14 270 250)">
        <ellipse cx="270" cy="250" rx="265" ry="36" fill="none" stroke="url(#ring)" stroke-width="3" opacity=".75"/>
      </g>
      <circle cx="270" cy="250" r="150" fill="url(#planet)"/>
      <g fill="#5350dc" opacity=".55">
        <ellipse cx="225" cy="195" rx="40" ry="13" transform="rotate(-22 225 195)"/>
        <ellipse cx="320" cy="270" rx="34" ry="10" transform="rotate(-18 320 270)"/>
        <ellipse cx="205" cy="290" rx="22" ry="8" transform="rotate(-20 205 290)"/>
        <ellipse cx="300" cy="180" rx="16" ry="6" transform="rotate(-25 300 180)"/>
      </g>
      <g transform="rotate(-14 270 250)">
        <path d="M5 250 A265 36 0 0 0 535 250" fill="none" stroke="url(#ring)" stroke-width="3.2"/>
      </g>
      <!-- mountains -->
      <path d="M330 440 L400 392 L470 410 L570 340 L650 380 L730 322 L810 296 L900 246 L965 206 L1035 258 L1105 236 L1200 300 L1200 440Z" fill="url(#mtnA)"/>
      <path d="M900 246 L965 206 L1035 258 L995 248 L965 262 L935 248Z" fill="#dcdcff" opacity=".92"/>
      <path d="M0 440 L0 396 L90 372 L180 398 L300 362 L420 394 L540 378 L660 404 L800 384 L940 410 L1080 390 L1200 414 L1200 440Z" fill="url(#mtnB)"/>
      <path d="M0 440 L0 424 Q200 404 400 428 T800 424 T1200 432 L1200 440Z" fill="#1c1793"/>
      <!-- towers + dome -->
      <g fill="#d5d4ff">
        <rect x="1078" y="330" width="4" height="72"/><ellipse cx="1080" cy="334" rx="17" ry="5"/><ellipse cx="1080" cy="322" rx="7" ry="9" fill="#b7b5ff"/>
        <rect x="1128" y="360" width="3" height="46"/><ellipse cx="1129.5" cy="363" rx="12" ry="4"/><ellipse cx="1129.5" cy="354" rx="5" ry="7" fill="#b7b5ff"/>
        <path d="M398 408 A22 22 0 0 1 442 408Z" fill="#c9c8ff"/>
      </g>
      <!-- ship -->
      <g transform="translate(985 96) rotate(8)">
        <polygon points="0,20 60,6 88,30 34,44" fill="#b9b6ff"/>
        <polygon points="60,6 96,-10 88,30" fill="#8f8cf6"/>
        <polygon points="34,44 88,30 60,52" fill="#6f6bea"/>
      </g>
    </svg>
  </div>
</header>

<div class="wrap">
  <section class="block" id="overview">
    <p class="about">
      The <b>subset construction</b> turns an NFA into an equivalent DFA whose states are <b>sets of NFA states</b>.
      It starts from the set <code>S</code> of initial states; the successor of a set <code>A</code> on a symbol <code>a</code>
      is the union of <code>&Delta;(q, a)</code> for every <code>q</code> in <code>A</code>. A set is final when it contains
      at least one final state of the NFA. Only the reachable sets are built.
    </p>
  </section>

  <section class="block">
    <h2 class="title">What you will find here</h2>
    <div class="features">
      <div class="feature">
        <div class="ico"><svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="#fff" stroke-width="1.6"><circle cx="5" cy="11" r="3"/><circle cx="17" cy="5" r="3"/><circle cx="17" cy="17" r="3"/><path d="M8 10 L14 6.2 M8 12 L14 15.8"/></svg></div>
        <h4>NFA diagram</h4><p>The original automaton</p>
      </div>
      <div class="feature">
        <div class="ico"><svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="#fff" stroke-width="1.6"><circle cx="5" cy="11" r="3"/><circle cx="17" cy="11" r="3"/><circle cx="17" cy="11" r="5.2" stroke-width="1"/><path d="M8.2 11 H11.6"/><path d="M10 9 L12 11 L10 13"/></svg></div>
        <h4>DFA diagram</h4><p>Reachable subsets only</p>
      </div>
      <div class="feature">
        <div class="ico"><svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="#fff" stroke-width="1.6"><rect x="3" y="4" width="16" height="14" rx="2"/><path d="M3 9 H19 M9 4 V18"/></svg></div>
        <h4>Transition tables</h4><p>State by symbol</p>
      </div>
      <div class="feature">
        <div class="ico"><svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round"><path d="M8 4 Q5 4 5 7 V9 Q5 11 3 11 Q5 11 5 13 V15 Q5 18 8 18"/><path d="M14 4 Q17 4 17 7 V9 Q17 11 19 11 Q17 11 17 13 V15 Q17 18 14 18"/></svg></div>
        <h4>Subset mapping</h4><p>DFA state to NFA set</p>
      </div>
    </div>
  </section>

  <section class="block" id="legend">
    <div class="card legend">
      <strong style="color:#fff;font-weight:500">How to read the diagrams</strong>
      <span class="item">
        <svg width="62" height="34" viewBox="0 0 62 34"><path d="M2 17 H24" stroke="#eeeeff" stroke-width="2"/><path d="M20 12.5 L27 17 L20 21.5Z" fill="#eeeeff"/><circle cx="43" cy="17" r="13" fill="#dcdcff" stroke="#7876f2" stroke-width="2"/></svg>
        Initial state
      </span>
      <span class="item">
        <svg width="40" height="34" viewBox="0 0 40 34"><circle cx="20" cy="17" r="15" fill="none" stroke="#4fbf8a" stroke-width="1.8"/><circle cx="20" cy="17" r="11" fill="#c2f4d5" stroke="#4fbf8a" stroke-width="2"/></svg>
        Final state (double ring)
      </span>
      <span class="item">
        <svg width="34" height="34" viewBox="0 0 34 34"><circle cx="17" cy="17" r="13" fill="#dcdcff" stroke="#7876f2" stroke-width="2"/></svg>
        Regular state
      </span>
      <span class="item">
        <svg width="34" height="34" viewBox="0 0 34 34"><circle cx="17" cy="17" r="13" fill="#c7c6ff" fill-opacity=".12" stroke="#9d9bd8" stroke-width="2" stroke-dasharray="5 4"/></svg>
        Empty set &#8709; (dead state)
      </span>
      <span class="item">
        <svg width="46" height="24" viewBox="0 0 46 24"><rect x="3" y="3" width="40" height="18" rx="7" fill="#141060" stroke="#5d59d9"/><text x="23" y="12" dy="0.35em" text-anchor="middle" font-family="monospace" font-size="12" font-weight="700" fill="#e4e3ff">a, b</text></svg>
        Symbols of the transition
      </span>
    </div>
  </section>

  <section class="block" id="cases">
    <h2 class="title">Results</h2>
    <div class="cases" id="cases-container"></div>
  </section>
</div>

<footer>
  Authors: <b>Dilan Acevedo Rivera</b> &amp; <b>Sim&oacute;n Santiago Soto Berrio</b> &middot; SI2002 Formal Languages
</footer>

<script>
const casesData = __CASES_DATA__;

/* ------------------------------------------------------------------ */
/*  Automaton drawing: Graphviz (dot, compiled to WebAssembly) lays out */
/*  the graph; the result is restyled to match the page.                */
/* ------------------------------------------------------------------ */
const COL = {
  edge: '#a9a7f7', chipFill: '#141060', chipStroke: '#5d59d9', chipText: '#e4e3ff',
  nodeFill: '#dcdcff', nodeStroke: '#7876f2', nodeText: '#1b1876',
  finalFill: '#c2f4d5', finalStroke: '#4fbf8a', finalText: '#0d4a30',
  deadFill: '#3a3690', deadStroke: '#9d9bd8', deadText: '#d5d4ff',
  start: '#eeeeff'
};
const FONT_STACK = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Courier New', monospace";

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmtSet = arr => arr.length ? '{' + arr.join(', ') + '}' : '\u2205';

/* Transition label drawn as a small rounded chip (Graphviz HTML-like label) */
function chipLabel(text) {
  const t = esc(text).replace(/ /g, '&#160;');
  return `<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="${COL.chipFill}" COLOR="${COL.chipStroke}" STYLE="ROUNDED"><TR><TD><FONT COLOR="${COL.chipText}" FACE="Courier-Bold" POINT-SIZE="12">&#160;${t}&#160;</FONT></TD></TR></TABLE>>`;
}

function buildDot(graph) {
  let dot = 'digraph G {\n';
  dot += '  graph [rankdir=LR, bgcolor="transparent", pad=0.4, nodesep=0.45, ranksep=0.7, splines=true];\n';
  dot += '  node [shape=circle, style=filled, fontname="Courier-Bold", fontsize=14, penwidth=2, fixedsize=true, width=0.62, height=0.62, margin=0];\n';
  dot += `  edge [color="${COL.edge}", penwidth=1.5, arrowsize=0.8];\n`;

  graph.nodes.forEach(n => {
    const fill = n.final ? COL.finalFill : n.dead ? COL.deadFill : COL.nodeFill;
    const stroke = n.final ? COL.finalStroke : n.dead ? COL.deadStroke : COL.nodeStroke;
    const text = n.final ? COL.finalText : n.dead ? COL.deadText : COL.nodeText;
    let label = `"${n.label}"`, extra = '';
    if (n.caption) {   // DFA state: number + the NFA subset it stands for
      label = `<<FONT FACE="Courier-Bold" POINT-SIZE="14">${esc(n.label)}</FONT><BR/><FONT FACE="Courier" POINT-SIZE="10">${esc(n.caption)}</FONT>>`;
      extra = ', shape=ellipse, fixedsize=false, margin="0.03,0.02"';
    }
    dot += `  n${n.id} [label=${label}, fillcolor="${fill}", color="${stroke}", fontcolor="${text}"` +
      `${n.final ? ', peripheries=2' : ''}${n.dead ? ', style="filled,dashed"' : ''}${extra}];\n`;
  });

  // Initial states go to the leftmost column
  const init = graph.nodes.filter(n => n.initial).map(n => 'n' + n.id);
  if (init.length) dot += `  { rank=min; ${init.join('; ')}; }\n`;

  graph.edges.forEach(e => {
    const loop = e.from === e.to ? ', tailport=n, headport=n' : '';
    dot += `  n${e.from} -> n${e.to} [label=${chipLabel(e.label)}${loop}];\n`;
  });
  return dot + '}\n';
}

/* Cleans the Graphviz SVG and adds the arrows that enter the initial states */
function finishSvg(svg, graph) {
  svg = svg.slice(svg.indexOf('<svg'));                       // drop <?xml ...> and DOCTYPE
  svg = svg.replace(/<!--[\s\S]*?-->\s*/g, '');

  // Where is every initial state? (Graphviz writes cx, cy, rx of its ellipses)
  const tr = svg.match(/translate\(([-\d.]+) ([-\d.]+)\)/);
  const tx = tr ? parseFloat(tr[1]) : 0;
  let arrows = '', leftMost = Infinity;
  graph.nodes.filter(n => n.initial).forEach(n => {
    const group = svg.match(new RegExp(`<title>n${n.id}</title>([\\s\\S]*?)</g>`));
    if (!group) return;
    const cx = parseFloat(group[1].match(/cx="([-\d.]+)"/)[1]);
    const cy = parseFloat(group[1].match(/cy="([-\d.]+)"/)[1]);
    const rx = Math.max(...[...group[1].matchAll(/rx="([-\d.]+)"/g)].map(m => parseFloat(m[1])));
    const tip = cx - rx - 1.5, x0 = tip - 34;
    leftMost = Math.min(leftMost, x0 + tx);
    arrows += `<path d="M${x0.toFixed(1)},${cy} L${(tip - 7).toFixed(1)},${cy}" fill="none" stroke="${COL.start}" stroke-width="2"/>` +
      `<polygon points="${tip.toFixed(1)},${cy} ${(tip - 9).toFixed(1)},${cy - 4.5} ${(tip - 9).toFixed(1)},${cy + 4.5}" fill="${COL.start}"/>`;
  });
  if (arrows) svg = svg.replace(/<\/g>\s*<\/svg>\s*$/, arrows + '</g></svg>');

  svg = svg.replace(/<title>[\s\S]*?<\/title>\s*/g, '');      // no tooltips like "n3"
  svg = svg.replace(/font-family="[^"]*"/g, `font-family="${FONT_STACK}"`);

  // viewBox: room for the initial arrows, and a minimum size so tiny graphs are not blown up
  const vbm = svg.match(/viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"/);
  let [vx, vy, vw, vh] = vbm.slice(1).map(Number);
  if (leftMost < vx + 6) { const extra = vx + 6 - leftMost; vx -= extra; vw += extra; }
  const MIN_W = 460, MIN_H = 320;
  if (vw < MIN_W) { vx -= (MIN_W - vw) / 2; vw = MIN_W; }
  if (vh < MIN_H) { vy -= (MIN_H - vh) / 2; vh = MIN_H; }
  svg = svg.replace(/<svg[^>]*>/, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vx.toFixed(1)} ${vy.toFixed(1)} ${vw.toFixed(1)} ${vh.toFixed(1)}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img" style="display:block">`);
  return svg;
}

function renderGraphSvg(viz, graph) {
  return finishSvg(viz.renderString(buildDot(graph), { format: 'svg', engine: 'dot' }), graph);
}

/* Pan (drag) and zoom (buttons, Ctrl + wheel) by editing the SVG viewBox */
function enableViewer(canvas, panel) {
  const svg = canvas.querySelector('svg');
  if (!svg) return;
  const b = svg.viewBox.baseVal;
  const home = { x: b.x, y: b.y, w: b.width, h: b.height };
  let vb = { ...home };
  const apply = () => svg.setAttribute('viewBox', `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  const unitsPerPx = () => { const r = svg.getBoundingClientRect(); return Math.max(vb.w / r.width, vb.h / r.height); };
  const toUnits = (cx, cy) => {
    const r = svg.getBoundingClientRect(), s = unitsPerPx();
    return { x: vb.x - (r.width * s - vb.w) / 2 + (cx - r.left) * s, y: vb.y - (r.height * s - vb.h) / 2 + (cy - r.top) * s };
  };
  const zoomAt = (factor, ux, uy) => {
    const nw = vb.w / factor, nh = vb.h / factor;
    vb = { x: ux - (ux - vb.x) * (nw / vb.w), y: uy - (uy - vb.y) * (nh / vb.h), w: nw, h: nh };
    apply();
  };
  panel.querySelectorAll('[data-zoom]').forEach(btn => btn.addEventListener('click', () => {
    const mode = btn.dataset.zoom;
    if (mode === 'reset') { vb = { ...home }; apply(); return; }
    zoomAt(mode === 'in' ? 1.25 : 1 / 1.25, vb.x + vb.w / 2, vb.y + vb.h / 2);
  }));
  const expandBtn = panel.querySelector('[data-expand]');
  if (expandBtn) expandBtn.addEventListener('click', () => panel.classList.toggle('wide'));
  canvas.addEventListener('wheel', ev => {
    if (!(ev.ctrlKey || ev.metaKey)) return;
    ev.preventDefault();
    const u = toUnits(ev.clientX, ev.clientY);
    zoomAt(ev.deltaY < 0 ? 1.15 : 1 / 1.15, u.x, u.y);
  }, { passive: false });
  let drag = null;
  canvas.addEventListener('mousedown', ev => { drag = { x: ev.clientX, y: ev.clientY, s: unitsPerPx() }; ev.preventDefault(); });
  window.addEventListener('mousemove', ev => {
    if (!drag) return;
    vb.x -= (ev.clientX - drag.x) * drag.s;
    vb.y -= (ev.clientY - drag.y) * drag.s;
    drag.x = ev.clientX; drag.y = ev.clientY;
    apply();
  });
  window.addEventListener('mouseup', () => { drag = null; });
}

function drawInto(viz, canvasId, graph) {
  const canvas = document.getElementById(canvasId);
  try {
    canvas.innerHTML = renderGraphSvg(viz, graph);
    enableViewer(canvas, canvas.closest('.panel'));
  } catch (err) {
    canvas.innerHTML = '<p class="msg err">The diagram could not be drawn: ' + esc(err.message || err) + '</p>';
  }
}

async function drawAllDiagrams() {
  const canvases = [...document.querySelectorAll('.canvas')];
  const fail = text => canvases.forEach(c => { c.innerHTML = `<p class="msg err">${text}</p>`; });
  if (typeof Viz === 'undefined') {
    fail('The layout library (Graphviz) could not be loaded. Check your internet connection and reload the page. The tables are still valid.');
    return;
  }
  let viz;
  try { viz = await Viz.instance(); } catch (err) { fail('The layout library (Graphviz) failed to start: ' + esc(err.message || err)); return; }
  casesData.forEach(c => {
    drawInto(viz, `nfa-net-${c.case_idx}`, c.nfa.graph);
    drawInto(viz, `dfa-net-${c.case_idx}`, c.dfa.graph);
  });
}

/* ------------------------------ tables ------------------------------ */
function tag(row) {
  if (row.is_start && row.is_final) return '<span class="tag both">start / final</span>';
  if (row.is_start) return '<span class="tag start">start</span>';
  if (row.is_final) return '<span class="tag final">final</span>';
  return '';
}

function buildTable(alphabet, rows, stateHeader, prefix, withSubset) {
  let head = `<th>${stateHeader}</th>`;
  if (withSubset) head += '<th>NFA subset</th>';
  alphabet.forEach(sym => { head += `<th>on <span class="sym">'${esc(sym)}'</span></th>`; });
  let body = '';
  rows.forEach(r => {
    let cells = `<td class="state">${prefix}${r.id}${tag(r)}</td>`;
    if (withSubset) cells += `<td>${esc(r.subset)}</td>`;
    alphabet.forEach(sym => { cells += `<td>${esc(r.transitions[sym] ?? '-')}</td>`; });
    body += `<tr>${cells}</tr>`;
  });
  return `<div class="tbl-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

/* ------------------------------- page -------------------------------- */
const chip = (label, value, cls = '') => `<span class="chip ${cls}"><strong>${label}</strong>${value}</span>`;

function panelHtml(kind, canvasId, title) {
  return `<div class="panel">
    <div class="panel-head">
      <span class="badge ${kind}">${kind.toUpperCase()}</span><h3>${title}</h3>
      <div class="zoom">
        <button type="button" data-zoom="in" title="Zoom in">+</button>
        <button type="button" data-zoom="out" title="Zoom out">&minus;</button>
        <button type="button" data-zoom="reset" title="Reset view">&#8634;</button>
        <button type="button" class="expand" data-expand title="Enlarge / shrink">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 1.5 H12.5 V5.5 M12.5 1.5 L8 6 M5.5 12.5 H1.5 V8.5 M1.5 12.5 L6 8"/></svg>
        </button>
      </div>
    </div>
    <div class="canvas" id="${canvasId}"><p class="msg">Drawing diagram&hellip;</p></div>
    <p class="hint">Drag to move. Buttons or Ctrl + scroll to zoom.</p>
  </div>`;
}

function renderCases() {
  const container = document.getElementById('cases-container');
  casesData.forEach(c => {
    const nfaId = `nfa-net-${c.case_idx}`, dfaId = `dfa-net-${c.case_idx}`;
    const article = document.createElement('article');
    article.className = 'card';
    article.id = `case-${c.case_idx}`;
    article.innerHTML = `
      <div class="case-head">
        <h3 class="case-title">Case ${c.case_idx}<small>${c.nfa.num_states} NFA states &rarr; ${c.dfa.table.length} DFA states</small></h3>
        <div class="chip-groups">
          <div class="chips">
            ${chip('Alphabet', c.alphabet.join(', '))}
            ${chip('NFA initial (S)', fmtSet(c.nfa.initial))}
            ${chip('NFA final (F)', fmtSet(c.nfa.final))}
          </div>
          <div class="chips">
            ${chip('DFA initial', c.dfa.initial, 'mint')}
            ${chip('DFA final', fmtSet(c.dfa.final), 'mint')}
          </div>
        </div>
      </div>
      <div class="panels">
        ${panelHtml('nfa', nfaId, 'N &mdash; the input automaton')}
        ${panelHtml('dfa', dfaId, 'M &mdash; reachable subset states')}
      </div>
      <div class="tables">
        <div><h3>Transition table of N</h3>${buildTable(c.alphabet, c.nfa.table, 'state', '', false)}</div>
        <div><h3>Transition table of M</h3>${buildTable(c.alphabet, c.dfa.table, 'state', '', true)}</div>
      </div>`;
    container.appendChild(article);
    // Big automata start enlarged (full width); small ones sit side by side
    [[nfaId, c.nfa.graph], [dfaId, c.dfa.graph]].forEach(([id, g]) => {
      if (g.nodes.length > 12) document.getElementById(id).closest('.panel').classList.add('wide');
    });
  });
  drawAllDiagrams();
}

document.addEventListener('DOMContentLoaded', renderCases);
</script>
</body>
</html>
"""
