#!/usr/bin/env python
"""walkthrough.py — the set-up and tear-down half of docs/walkthrough.md, as one command.

    python tools/walkthrough.py stage     # check the pin, convert TORIVA's parquet to .xpt, stage the study,
                                          # chains and the M.MMRM implementation into the app
    python tools/walkthrough.py serve     # 'stage', then serve the app (threaded; not serve.py) until Ctrl-C, then 'clean'
    python tools/walkthrough.py clean     # remove everything staged; the submodule is clean at its pin again
    python tools/walkthrough.py html      # write docs/walkthrough.md as a standalone HTML page (also served at /walkthrough)

Options: --toriva <path> (default: a sibling checkout named torivumab-nsclc-301); --port (default 8080).

CDISC Library: put a Library account's API key in a file named .cdisc-api-key in the repository root
(git-ignored) or in your home directory — one line, the key — or set CDISC_API_KEY. Then the app's
concept *Reference* links open the SDTM dataset specialization through a proxy at /cdisc-library/
that adds the key. Without a key the links point at the Library API directly and answer 401.

What it does not do is the clicking: steps 1–8 of the walkthrough are yours. The Load button and
alert() freeze browser automation, so nothing here drives the page either.

The staged files live inside the pinned, read-only submodule (ac-dc-app/data/usdm/studies.json is
edited; new files are added under ac-dc-app/data/). 'clean' reverts the edit and deletes the files,
and refuses to finish while `git status` inside the submodule is not empty.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "upstream" / "analysis-concepts"
APP = SUB / "ac-dc-app"
STAGED = APP / "data" / "toriva"
USDM_SRC = ROOT / "study" / "usdm" / "toriva-lung-301.usdm.json"
USDM_DST = APP / "data" / "usdm" / "toriva-lung-301.usdm.json"
STUDIES = APP / "data" / "usdm" / "studies.json"
CHAINS = {
    "lab-chain.json": ROOT / "endpoints" / "01-simple-lab-cfb" / "chain.json",
    "chain-mmrm.json": ROOT / "endpoints" / "04-vitals-cfb-mmrm" / "chain-mmrm.json",
    "chain-ancova.json": ROOT / "endpoints" / "04-vitals-cfb-mmrm" / "chain.json",
    "r_impl_mmrm.json": ROOT / "endpoints" / "04-vitals-cfb-mmrm" / "r_impl_mmrm.json",
}
INDUCTION = ["Baseline", "C1D15", "C2D1", "C3D1", "C4D1", "C5D1", "C6D1"]
LIBRARY = "https://api.library.cdisc.org/api/cosmos/v2/"
PROXY = "/cdisc-library/"  # served by `serve`: forwards to LIBRARY with the api-key header from CDISC_API_KEY
KEY_FILES = (ROOT / ".cdisc-api-key", Path.home() / ".cdisc-api-key")  # both git-ignored / outside the repo


def read_api_key() -> str:
    """CDISC_API_KEY from the environment, else the first line of .cdisc-api-key in the repository root or the home directory."""
    env = os.environ.get("CDISC_API_KEY", "").strip()
    if env:
        return env
    for f in KEY_FILES:
        if f.is_file():
            key = f.read_text(encoding="utf-8").strip().splitlines()[0].strip() if f.read_text(encoding="utf-8").strip() else ""
            if key:
                return key
    return ""


API_KEY = read_api_key()


for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def say(msg: str) -> None:
    print(msg, flush=True)


OWN = ("ac-dc-app/data/usdm/studies.json", "ac-dc-app/data/usdm/toriva-lung-301.usdm.json", "ac-dc-app/data/toriva/")


def foreign_dirt() -> str:
    """Submodule status lines that are not this script's own staged files."""
    lines = [l for l in git("status", "--short").splitlines() if l.strip()]
    def path_of(l: str) -> str:  # 'XY path' — XY may begin with a space, and the first line may have lost it to strip()
        parts = l.strip().split(None, 1)
        return parts[1].strip() if len(parts) == 2 else ""
    return "\n".join(l for l in lines if not any(path_of(l).startswith(o) for o in OWN))


def git(*args: str, cwd: Path = SUB) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True).stdout.strip()


def port_owner(port: int = 8080) -> str | None:
    """PID of whatever is listening on the port, or None. Windows netstat and POSIX lsof/ss."""
    try:
        if os.name == "nt":
            out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=15).stdout
            for line in out.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    return line.split()[-1]
        else:
            out = subprocess.run(["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"], capture_output=True, text=True, timeout=15).stdout.strip()
            return out.splitlines()[0] if out else None
    except (OSError, subprocess.SubprocessError):
        return None
    return None


WALKTHROUGH_MD = ROOT / "docs" / "walkthrough.md"


def render_markdown(md: str) -> str:
    """The subset docs/walkthrough.md uses: #/## headings, paragraphs, - and 1. lists (nested by indent), ``` fences,
    > quotes, **bold**, *italic*, `code`, [text](url). No Markdown library is assumed to be installed."""
    import html as _h
    import re as _re

    def inline(s: str) -> str:
        s = _h.escape(s, quote=False)
        s = _re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = _re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        # ![caption](media/...) — a screenshot of the app, with its caption beneath. Before the link
        # rule, which would otherwise eat the same brackets (LG, 2026-10-02: the page should show
        # which menu to pick, not only name it).
        s = _re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                    r'<figure class="shot"><img src="\2" alt="\1" loading="lazy"><figcaption>\1</figcaption></figure>', s)
        s = _re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        return s

    # pre-pass: absorb a list item's wrapped continuation lines (indented, not a fence, not another item, not blank)
    raw = md.split("\n"); lines = []
    for line in raw:
        if lines and _re.match(r"^\s+\S", line) and not _re.match(r"^\s*(```|[-*]\s|\d+\.\s|>)", line) \
                and _re.match(r"^\s*([-*]|\d+\.)\s", lines[-1]) and not lines[-1].rstrip().endswith("```"):
            lines[-1] = lines[-1] + " " + line.strip()
        else:
            lines.append(line)
    out, i = [], 0
    list_stack: list[tuple[int, str]] = []  # (indent, tag)

    def close_lists(to_indent: int = -1):
        while list_stack and list_stack[-1][0] > to_indent:
            out.append(f"</li></{list_stack.pop()[1]}>")

    para: list[str] = []
    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>"); para.clear()

    CALLOUT_LABELS = {"why": "Why this matters", "note": "Note", "history": "History", "result": "What you should see",
                      "warn": "Watch out", "details": "Details"}
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        m_c = _re.match(r"^:::\s*(\w+)(?:\s+(.*?))?\s*$", stripped)
        if m_c and m_c.group(1) in CALLOUT_LABELS:
            flush_para(); close_lists()
            kind, title = m_c.group(1), (m_c.group(2) or CALLOUT_LABELS[m_c.group(1)]).strip()
            inner, depth = [], 1
            i += 1
            while i < len(lines):
                t = lines[i].strip()
                m_open = _re.match(r"^:::\s*(\w+)", t)
                if m_open and m_open.group(1) in CALLOUT_LABELS:
                    depth += 1
                elif t == ":::":
                    depth -= 1
                    if depth == 0:
                        i += 1; break
                inner.append(lines[i]); i += 1
            body = render_markdown("\n".join(inner))
            if kind == "details":
                out.append(f'<details class="callout details"><summary>{inline(title)}</summary><div class="callout-body">{body}</div></details>')
            else:
                out.append(f'<aside class="callout {kind}"><p class="callout-label">{inline(title)}</p>{body}</aside>')
            continue
        m_fence = _re.match(r"^(\s*)```(\w*)\s*$", line)
        if m_fence:
            flush_para()
            indent = len(m_fence.group(1)); code = []
            i += 1
            while i < len(lines) and not _re.match(r"^\s*```\s*$", lines[i]):
                code.append(lines[i][indent:] if lines[i].startswith(" " * indent) else lines[i]); i += 1
            i += 1
            if indent == 0:
                close_lists()
            out.append("<pre><code>" + _h.escape("\n".join(code)) + "</code></pre>")
            continue
        m_h = _re.match(r"^(#{1,3})\s+(.*)$", line)
        if m_h:
            flush_para(); close_lists()
            lvl = len(m_h.group(1)); text = m_h.group(2).strip()
            anchor = _re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            m_step = _re.match(r"^(\d+)\.\s+(.*)$", text) if lvl == 2 else None
            if m_step:
                out.append(f'<h2 id="{anchor}" class="step"><span class="step-no">{m_step.group(1)}</span>{inline(m_step.group(2))}</h2>')
            else:
                out.append(f'<h{lvl} id="{anchor}">{inline(text)}</h{lvl}>')
            i += 1; continue
        m_li = _re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m_li:
            flush_para()
            indent = len(m_li.group(1)); tag = "ol" if m_li.group(2)[0].isdigit() else "ul"
            if list_stack and list_stack[-1][0] == indent:
                out.append("</li><li>" + inline(m_li.group(3)))
            elif not list_stack or indent > list_stack[-1][0]:
                list_stack.append((indent, tag)); out.append(f"<{tag}><li>" + inline(m_li.group(3)))
            else:
                close_lists(indent); out.append("</li><li>" + inline(m_li.group(3)))
            i += 1; continue
        if stripped.startswith(">"):
            flush_para(); close_lists()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(_re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append("<blockquote>" + render_markdown("\n".join(q)) + "</blockquote>"); continue
        if not stripped:
            flush_para()
            # a blank line ends a list only if the next non-blank line is not indented list content
            j = i + 1
            while j < len(lines) and not lines[j].strip(): j += 1
            if j >= len(lines) or not (lines[j].startswith(" ") or _re.match(r"^\s*([-*]|\d+\.)\s", lines[j])):
                close_lists()
            i += 1; continue
        if list_stack and line.startswith(" "):
            out.append(" " + inline(stripped)); i += 1; continue  # continuation inside a list item
        para.append(line); i += 1
    flush_para(); close_lists()
    return "\n".join(out)


PAGE_CSS = """
body{font:16px/1.55 -apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1f2328;background:#fff;margin:0;padding:24px 16px 64px}
main{max-width:820px;margin:0 auto} h1{font-size:1.6em;margin:.2em 0 .6em} h2{font-size:1.25em;margin:1.6em 0 .5em;border-bottom:1px solid #d0d7de;padding-bottom:.2em}
h3{font-size:1.05em;margin:1.2em 0 .4em} p,li{margin:.4em 0} ul,ol{padding-left:1.4em} li>ul,li>ol{margin:.2em 0}
code{font:.92em ui-monospace,Consolas,'Courier New',monospace;background:#f6f8fa;padding:.1em .3em;border-radius:4px}
pre{background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:12px;overflow:auto} pre code{background:none;padding:0}
blockquote{border-left:4px solid #d0d7de;margin:.8em 0;padding:.2em 1em;color:#57606a;background:#fafbfc}
a{color:#0969da} .note{color:#57606a;font-size:.9em;margin-bottom:1.5em}
@media (prefers-color-scheme:dark){body{color:#e6edf3;background:#0d1117} h2{border-color:#30363d} code,pre{background:#161b22;border-color:#30363d} blockquote{color:#8b949e;background:#0d1117;border-color:#30363d} a{color:#58a6ff} .note{color:#8b949e}}
"""

# The walkthrough page's own layout: a sticky step navigator beside the text, typed
# callouts, a header with the pins, copy buttons on commands. Additive to PAGE_CSS.
WALKTHROUGH_CSS = """
:root{--ink:#1f2328;--muted:#57606a;--line:#d0d7de;--panel:#f6f8fa;--accent:#0969da;--why:#7a4f01;--why-bg:#fff8e6;--hist:#57606a;--hist-bg:#f6f8fa;--res:#116329;--res-bg:#eefaf1;--warn:#a40e26;--warn-bg:#fff0f2}
body{padding:0}
.top{border-bottom:1px solid var(--line);background:var(--panel)}
.top-in{max-width:1180px;margin:0 auto;padding:22px 24px 18px}
.kicker{font-size:.8em;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 .3em}
.top h1{font-size:1.75em;line-height:1.2;margin:0 0 .5em}
.lead{max-width:760px;color:var(--ink);margin:0 0 .9em;font-size:1.02em}
.facts{display:flex;flex-wrap:wrap;gap:8px 22px;margin:0;padding:0;list-style:none;font-size:.9em;color:var(--muted)}
.facts strong{color:var(--ink);font-weight:600} .facts code{font-size:.95em}
.layout{max-width:1180px;margin:0 auto;padding:24px 24px 80px;display:grid;grid-template-columns:230px minmax(0,1fr);gap:40px;align-items:start}
nav.steps{position:sticky;top:18px;font-size:.9em}
nav.steps .nav-title{font-size:.78em;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 .6em}
nav.steps ol{list-style:none;margin:0;padding:0;border-left:2px solid var(--line)}
nav.steps li a{display:block;padding:.3em .8em;color:var(--muted);text-decoration:none;border-left:2px solid transparent;margin-left:-2px;line-height:1.3}
nav.steps li a:hover{color:var(--ink)} nav.steps li a.current{color:var(--accent);border-left-color:var(--accent);font-weight:600}
nav.steps .n{display:inline-block;min-width:1.4em;color:var(--muted);font-variant-numeric:tabular-nums}
main{max-width:none;min-width:0}
h2.step{display:flex;align-items:center;gap:.6em;border:0;padding:0;margin:2.2em 0 .6em;font-size:1.35em}
h2,h3{scroll-margin-top:16px}
.step-no{display:inline-flex;align-items:center;justify-content:center;width:1.7em;height:1.7em;border-radius:50%;background:var(--accent);color:#fff;font-size:.72em;font-weight:700;flex:none}
.callout{border:1px solid var(--line);border-left-width:4px;border-radius:6px;padding:.7em 1em .5em;margin:1em 0;background:var(--panel)}
.callout-label{margin:0 0 .3em!important;font-size:.78em;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.callout.why{border-left-color:var(--why);background:var(--why-bg)} .callout.why .callout-label{color:var(--why)}
.callout.history{border-left-color:var(--line);background:var(--hist-bg);color:var(--hist);font-size:.93em} .callout.history .callout-label{color:var(--hist)}
.callout.result{border-left-color:var(--res);background:var(--res-bg)} .callout.result .callout-label{color:var(--res)}
.callout.warn{border-left-color:var(--warn);background:var(--warn-bg)} .callout.warn .callout-label{color:var(--warn)}
.callout.note{border-left-color:var(--accent)}
details.callout summary{cursor:pointer;font-weight:600;list-style:none} details.callout summary::before{content:"\\25B8  ";color:var(--muted)} details[open].callout summary::before{content:"\\25BE  "}
details.callout summary::-webkit-details-marker{display:none} .callout-body{margin-top:.6em}
figure.shot{margin:.9em 0 1.2em} figure.shot img{display:block;max-width:100%;border:1px solid var(--line);border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.08)} figure.shot figcaption{font-size:.86em;color:var(--muted);margin-top:.45em}
pre{position:relative;padding-right:64px} .copy{position:absolute;top:8px;right:8px;font:12px system-ui;padding:3px 8px;border:1px solid var(--line);border-radius:4px;background:#fff;color:var(--muted);cursor:pointer} .copy:hover{color:var(--ink)}
@media (max-width:900px){.layout{grid-template-columns:1fr;gap:16px} nav.steps{position:static;border-bottom:1px solid var(--line);padding-bottom:12px} nav.steps ol{border:0;display:flex;flex-wrap:wrap;gap:2px 10px} nav.steps li a{border:0;padding:.2em .3em}}
@media (prefers-color-scheme:dark){:root{--ink:#e6edf3;--muted:#8b949e;--line:#30363d;--panel:#161b22;--accent:#58a6ff;--why:#e3b341;--why-bg:#2a2210;--hist:#8b949e;--hist-bg:#161b22;--res:#3fb950;--res-bg:#12261a;--warn:#ff7b72;--warn-bg:#2d1418} .copy{background:#0d1117}}
"""

WALKTHROUGH_JS = """
document.querySelectorAll('pre').forEach(function(pre){
  var b=document.createElement('button');b.className='copy';b.type='button';b.textContent='Copy';
  b.addEventListener('click',function(){navigator.clipboard.writeText(pre.querySelector('code').innerText).then(function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1200)})});
  pre.appendChild(b)});
var links=[].slice.call(document.querySelectorAll('nav.steps a'));
var heads=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1))}).filter(Boolean);
function mark(){var y=window.scrollY+80,cur=heads[0];heads.forEach(function(h){if(h.offsetTop<=y)cur=h});
  links.forEach(function(a){a.classList.toggle('current',cur&&a.getAttribute('href')==='#'+cur.id})}
window.addEventListener('scroll',mark,{passive:true});mark();
"""


OVERLAY_JS = r"""
// walkthrough overlay — served by tools/walkthrough.py, not part of the upstream app.
// 1. '(no filter)' on every slice-value dropdown: the engine treats an empty value as no filter, but the app's
//    dropdowns offer only the values it found, so a contrast label like 'Torivumab vs Placebo' can never be cleared.
// 2. Register endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json as the M.MMRM implementation once the app has loaded.
// 3. Install the mmrm package once the WebR engine is initialised (the engine does not act on 'packages').
(function () {
  const NOFILTER = '__nofilter__';
  function status(msg, ms) {
    let el = document.getElementById('wt-overlay-status');
    if (!el) { el = document.createElement('div'); el.id = 'wt-overlay-status';
      el.style.cssText = 'position:fixed;right:12px;bottom:12px;z-index:9999;background:#1f2937;color:#fff;padding:8px 12px;border-radius:6px;font:13px system-ui;max-width:420px;box-shadow:0 2px 8px rgba(0,0,0,.3)';
      document.body.appendChild(el); }
    el.textContent = 'walkthrough: ' + msg; el.style.display = 'block';
    if (ms) setTimeout(() => { el.style.display = 'none'; }, ms);
  }
  function addNoFilter() {
    for (const sel of document.querySelectorAll('select.exec-slice-val-override')) {
      if (!sel.querySelector('option[data-wt="' + NOFILTER + '"]')) {
        const opt = document.createElement('option'); opt.value = ''; opt.textContent = '(no filter — keep all values)'; opt.dataset.wt = NOFILTER;
        sel.insertBefore(opt, sel.firstChild);
      }
      // whenever the override for this dimension is empty, the dropdown must show it — the app re-renders the select on
      // every run and the browser would otherwise display the first app option while no filter is applied
      const st = window.appState, dim = sel.dataset.dim, slice = sel.dataset.slice || 'endpoint';
      const ep = st && (st.currentEndpointId || (st.selectedEndpoints || [])[0]);
      const ov = ep && st.endpointResults && st.endpointResults[ep] && st.endpointResults[ep].sliceOverrides;
      const o = ov && (ov[slice + '|' + dim] || ov['endpoint|' + dim]);
      if (o && o.value === '' && sel.value !== '') sel.value = '';
    }
  }
  new MutationObserver(addNoFilter).observe(document.documentElement, { childList: true, subtree: true });
  addNoFilter();

  async function registerMmrm() {
    const st = window.appState; if (!st) return false;
    if (!st.loaded) return false;
    try {
      st.methodImplementationCatalog = st.methodImplementationCatalog || { implementations: {} };
      st.methodImplementationCatalog.implementations = st.methodImplementationCatalog.implementations || {};
      if (!st.methodImplementationCatalog.implementations['M.MMRM']) {
        const impl = await (await fetch('/ac-dc-app/data/toriva/r_impl_mmrm.json')).json();
        st.methodImplementationCatalog.implementations['M.MMRM'] = [impl];
        status('M.MMRM implementation registered (r_impl_mmrm.json)', 6000);
      }
      return true;
    } catch (e) { status('could not register M.MMRM: ' + e, 8000); return true; }
  }
  let mmrmInstalled = false, installing = false;
  async function installMmrm() {
    if (mmrmInstalled || installing) return;
    try {
      const eng = await import('/ac-dc-app/js/utils/webr-engine.js');
      if (!eng.isInitialized()) return;
      installing = true; status('installing the mmrm package in WebR (about half a minute) …');
      const out = await eng.executeR('webr::install("mmrm"); as.character(requireNamespace("mmrm", quietly = TRUE))');
      const ok = JSON.stringify(out).includes('TRUE');
      mmrmInstalled = ok; status(ok ? 'mmrm package installed — the MMRM pass can execute' : 'mmrm install did not confirm: ' + JSON.stringify(out).slice(0, 120), ok ? 8000 : 0);
    } catch (e) { status('mmrm install failed: ' + e, 0); } finally { installing = false; }
  }
  let registered = false;
  setInterval(async () => { if (!registered) registered = await registerMmrm(); if (!mmrmInstalled) installMmrm(); }, 2000);
})();
"""


def render_library_html(obj: dict, path: str) -> bytes:
    """A CDISC Library dataset specialization or biomedical concept as a page: header facts, the variables table, raw link."""
    import html as _h
    e = lambda s: _h.escape("" if s is None else str(s), quote=False)
    links = obj.get("_links", {}) or {}
    title = obj.get("shortName") or obj.get("datasetSpecializationId") or obj.get("conceptId") or path
    facts = []
    for k in ("datasetSpecializationId", "domain", "source", "sdtmigStartVersion", "sdtmigEndVersion", "conceptId", "ncitCode", "definition", "categories", "synonyms"):
        v = obj.get(k)
        if v not in (None, "", []):
            facts.append((k, ", ".join(map(str, v)) if isinstance(v, list) else str(v)))
    for name, l in links.items():
        if isinstance(l, dict) and l.get("href") and name != "self":
            href = l["href"]; href = (PROXY + href.lstrip("/")) if href.startswith("/mdr/") else href
            facts.append((name, f'<a href="{e(href)}">{e(l.get("title") or l["href"])}</a> <span class="dim">({e(l.get("type"))})</span>'))
    rows = []
    for v in obj.get("variables", []) or []:
        cl = v.get("codelist") or {}; at = v.get("assignedTerm") or {}; rel = v.get("relationship") or {}
        vals = v.get("valueList") or []
        rows.append("<tr>" + "".join(f"<td>{x}</td>" for x in (
            f"<code>{e(v.get('name'))}</code>", e(v.get("role")),
            e(v.get("dataType")) + (f" ({v.get('length')})" if v.get("length") else ""),
            (f'<a href="{e(cl.get("href"))}">{e(cl.get("submissionValue") or cl.get("conceptId"))}</a>' if cl.get("href") else e(cl.get("submissionValue") or "")) if cl else "",
            (e(at.get("value")) + (f' <span class="dim">{e(at.get("conceptId"))}</span>' if at.get("conceptId") else "")) if at else (", ".join(map(e, vals)) if vals else ""),
            ("required" if v.get("mandatoryVariable") else "") + (" · value required" if v.get("mandatoryValue") else ""),
            e(" / ".join(x for x in (v.get("originType"), v.get("originSource")) if x)),
            e(f"{rel.get('subject','')} {rel.get('linkingPhrase','')} {rel.get('object','')}".strip()) if rel else "",
        )) + "</tr>")
    table = ("<table><thead><tr><th>Variable</th><th>Role</th><th>Type</th><th>Codelist</th><th>Assigned term / values</th><th>Mandatory</th><th>Origin</th><th>Relationship</th></tr></thead>"
             "<tbody>" + "".join(rows) + "</tbody></table>") if rows else "<p class=\"dim\">No variables in this document.</p>"
    facts_html = "".join(f"<dt>{e(k)}</dt><dd>{v if v.startswith('<a ') else e(v)}</dd>" for k, v in facts)
    page = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{e(title)} — CDISC Library</title><style>{PAGE_CSS}"
            "table{border-collapse:collapse;width:100%;font-size:.92em} th,td{border:1px solid #d0d7de;padding:5px 8px;text-align:left;vertical-align:top} th{background:#f6f8fa}"
            "dl{display:grid;grid-template-columns:max-content 1fr;gap:.25em 1em} dt{font-weight:600} .dim{color:#57606a}"
            "@media (prefers-color-scheme:dark){th{background:#161b22} th,td{border-color:#30363d} .dim{color:#8b949e}}</style></head><body><main>"
            f"<p class=\"note\">CDISC Library, fetched through the walkthrough server with your key — <a href=\"?raw=1\">raw JSON</a></p>"
            f"<h1>{e(title)}</h1><dl>{facts_html}</dl>{table}</main></body></html>")
    return page.encode("utf-8")


def walkthrough_page(port: int = 8080, media_base: str | None = None) -> bytes:
    """docs/walkthrough.md as a page. Everything above the first '---' rule is the header: the H1
    is the title, plain paragraphs the lead, '- **Label**' bullets the at-a-glance facts. The H2s
    below the rule become the step navigator; '## N. Title' headings get their number as a badge."""
    import html as _h
    md = WALKTHROUGH_MD.read_text(encoding="utf-8")
    head, _, rest = md.partition("\n---\n")
    if not rest:
        head, rest = "", md
    title, lead_lines, facts = "Walkthrough", [], []
    for line in head.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif re.match(r"^- \*\*.+?\*\*", line):
            facts.append(line[2:].strip())
        elif line.strip():
            lead_lines.append(line.strip())
    steps = []
    for m in re.finditer(r"^## (.*)$", rest, re.M):
        text = m.group(1).strip()
        anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        m_step = re.match(r"^(\d+)\.\s+(.*)$", text)
        steps.append((anchor, m_step.group(1) if m_step else "", m_step.group(2) if m_step else text))

    def inline(t: str) -> str:
        return render_markdown(t).replace("<p>", "").replace("</p>", "")

    nav = "".join(f'<li><a href="#{a}"><span class="n">{n}</span>{_h.escape(t)}</a></li>' for a, n, t in steps)
    facts_html = "".join(f"<li>{inline(f)}</li>" for f in facts)
    page = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{_h.escape(title)}</title><style>{PAGE_CSS}{WALKTHROUGH_CSS}</style></head><body>"
            "<header class=\"top\"><div class=\"top-in\"><p class=\"kicker\">Hands-on walkthrough · rendered from <code>docs/walkthrough.md</code></p>"
            f"<h1>{_h.escape(title)}</h1>"
            + (f"<p class=\"lead\">{inline(' '.join(lead_lines))}</p>" if lead_lines else "")
            + (f"<ul class=\"facts\">{facts_html}</ul>" if facts else "")
            + "</div></header><div class=\"layout\">"
            f"<nav class=\"steps\"><p class=\"nav-title\">Steps</p><ol>{nav}</ol>"
            f"<p style=\"margin-top:1em\"><a href=\"http://localhost:{port}/ac-dc-app/index.html\" target=\"_blank\">Open the app ↗</a>"
            f"<br><small>served by <code>walkthrough.py serve</code> on port {port}</small></p></nav>"
            f"<main>{render_markdown(rest)}</main></div><script>{WALKTHROUGH_JS}</script></body></html>")
    # The markdown links docs/media/ relatively, which is right on GitHub and wrong here. Served, the
    # links go to the server's /media/ route; written as a file, to docs/media on disk, so the
    # screenshots show with no server running (the "no server needed" promise of `html`).
    base = media_base if media_base is not None else f"http://localhost:{port}/media/"
    page = page.replace('href="media/', f'href="{base}')
    page = page.replace('src="media/', f'src="{base}')
    return page.encode("utf-8")


def html(args: argparse.Namespace) -> None:
    out = Path(args.out) if args.out else Path(os.environ.get("TEMP", ".")) / "walkthrough.html"
    out.write_bytes(walkthrough_page(getattr(args, "port", 8080), media_base=(ROOT / "docs" / "media").as_uri() + "/"))
    say(f"wrote {out} — open it in a browser (no server needed)")


def find_toriva(arg: str | None) -> Path:
    for cand in (arg, os.environ.get("TORIVA_DIR"), str(ROOT.parent / "torivumab-nsclc-301")):
        if cand and (Path(cand) / "datasets" / "adam" / "adsl.parquet").is_file():
            return Path(cand)
    sys.exit("TORIVA checkout not found: pass --toriva, set TORIVA_DIR, or clone it beside this repository")


def check_pin(tor: Path) -> None:
    pin = re.search(r"\| Commit \| `([0-9a-f]{40})`", (ROOT / "study" / "source-refs.md").read_text(encoding="utf-8"))
    head = git("rev-parse", "HEAD", cwd=tor)
    if pin and head == pin.group(1):
        say(f"pin OK: TORIVA checkout at {head[:8]}, as study/source-refs.md pins")
    else:
        say(f"WARNING: TORIVA checkout at {head[:8]} but study/source-refs.md pins {pin.group(1)[:8] if pin else '?'} — "
            "the numbers in the walkthrough are for the pin; re-pin deliberately (CLAUDE.md) or check out the pin")
    sub_head = git("rev-parse", "HEAD")
    dirt = git("status", "--short")
    state = "clean" if not dirt else ("only this script's staged files present" if not foreign_dirt() else "NOT CLEAN — foreign changes, fix by hand")
    say(f"submodule at {sub_head[:7]} ({state})")


def to_xpt(tor: Path) -> None:
    try:
        import pyarrow.parquet as pq  # noqa: WPS433 — optional dependency, only for stage
        import pyreadstat
    except ImportError as exc:
        import _deps
        sys.exit(f"{_deps.hint(exc.name or 'pyarrow')}")

    adam = tor / "datasets" / "adam"
    STAGED.mkdir(parents=True, exist_ok=True)

    def write(name: str, df, fname: str) -> None:
        for c in df.columns:
            if str(df[c].dtype) in ("object", "str", "string"):
                df[c] = df[c].astype(str).where(df[c].notna(), None)
        pyreadstat.write_xport(df, str(STAGED / fname), file_format_version=5, table_name=name.upper())
        say(f"  {fname}: {len(df)} rows")

    for name in ("adsl", "adlb"):
        write(name, pq.ParquetFile(adam / f"{name}.parquet").read().to_pandas(), f"{name}.xpt")
    advs = pq.ParquetFile(adam / "advs.parquet").read().to_pandas()
    present = [v for v in INDUCTION if v in set(advs["AVISIT"])]
    write("advs", advs[advs["AVISIT"].isin(present)].copy(), "advs_induction.xpt")
    say(f"  induction window: {', '.join(present)}")


def stage(args: argparse.Namespace) -> None:
    tor = find_toriva(args.toriva)
    check_pin(tor)
    if foreign_dirt():
        sys.exit("the submodule carries changes that are not this script's:\n" + foreign_dirt() + "\nit must be clean at its pin (CLAUDE.md) — fix by hand")
    say("converting TORIVA's ADaM to .xpt (adsl, adlb, advs induction window) — about a minute for adlb ...")
    to_xpt(tor)
    for dst, src in CHAINS.items():
        shutil.copy2(src, STAGED / dst)
    if API_KEY:
        # the app renders each concept's `reference` as a link; with a key, route it through the proxy so the
        # link opens the specialization. The repository's fragment keeps the true Library URI — only the staged copy changes.
        frag = json.loads(USDM_SRC.read_text(encoding="utf-8"))
        n = 0
        for b in frag["study"]["versions"][0].get("biomedicalConcepts", []):
            r = b.get("reference") or ""
            if r.startswith(LIBRARY):
                b["reference"] = PROXY + r[len(LIBRARY):]; n += 1
        USDM_DST.write_text(json.dumps(frag, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        say(f"CDISC_API_KEY set: {n} concept references routed through {PROXY} (the staged copy only)")
    else:
        shutil.copy2(USDM_SRC, USDM_DST)
        say("no CDISC Library key (CDISC_API_KEY, or .cdisc-api-key in the repository root or your home directory): "
            "concept Reference links point at the Library API directly and will answer 401")
    manifest = json.loads(STUDIES.read_text(encoding="utf-8"))
    entries = manifest if isinstance(manifest, list) else manifest["studies"]
    if not any(e.get("file") == USDM_DST.name for e in entries):
        entries.append({"file": USDM_DST.name})
    STUDIES.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    say(f"staged: {USDM_DST.name} + manifest entry, {len(CHAINS)} chain/implementation files, 3 .xpt files under ac-dc-app/data/")
    say("""
In the app (http://localhost:8080/ac-dc-app/index.html) the study card is TORIVA-LUNG 301.
Step 8 data: upload from ac-dc-app/data/toriva/ (adsl.xpt, adlb.xpt; advs_induction.xpt for the vitals pass).
Served by `serve`, the page carries an overlay: a '(no filter)' entry in every slice dropdown, the M.MMRM
implementation registered on load, the mmrm package installed once the WebR engine is up (status box, bottom right).
To load a saved chain without the Load button (it opens a native picker), in the browser console:

  const ser = await import('/ac-dc-app/js/utils/instance-serializer.js');
  ser.deserializeStudyInstance(await (await fetch('/ac-dc-app/data/toriva/lab-chain.json')).json(), window.appState);
""")


def clean(_: argparse.Namespace | None = None) -> None:
    subprocess.run(["git", "-C", str(SUB), "checkout", "--", "ac-dc-app/data/usdm/studies.json"], check=False)
    if USDM_DST.exists():
        USDM_DST.unlink()
    if STAGED.exists():
        import time
        for attempt in range(6):  # a serve or stage still writing an .xpt holds the file for a moment on Windows
            try:
                shutil.rmtree(STAGED); break
            except PermissionError as e:
                if attempt == 5:
                    sys.exit(f"cannot remove {STAGED}: {e}\nis a `walkthrough.py serve` or `stage` still running? stop it, then run clean again")
                say("  a staged file is still in use; waiting ..."); time.sleep(5)
    status = git("status", "--short")
    if status:
        sys.exit(f"the submodule is still not clean:\n{status}\nfix by hand — it must be clean at its pin")
    say(f"clean: submodule at {git('rev-parse', 'HEAD')[:7]}, nothing staged")


def serve(args: argparse.Namespace) -> None:
    port = getattr(args, "port", 8080)
    owner = port_owner(port)
    if owner:
        sys.exit(f"port {port} is already in use (PID {owner}) — a previous serve is still running. Stop it first "
                 f"(Windows: taskkill /PID {owner} /F) or pass --port, then run this again. Nothing was staged.")
    stage(args)
    say(f"serving http://localhost:{port}/ac-dc-app/index.html — the guide is at http://localhost:{port}/walkthrough — Ctrl-C to stop and clean up")
    # Not upstream's serve.py: that is the single-threaded HTTPServer with a listen backlog of 5, and the app
    # fires ~22 fetches at once on load — on Windows some are dropped and the page says "Failed to load data"
    # (seen 2026-09-20). Same root, same no-cache headers, threading server.
    import functools
    import http.server

    class NoCache(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()

        def log_message(self, fmt, *a):  # one line per request, like serve.py, without the date noise
            sys.stderr.write("%s %s\n" % (self.address_string(), fmt % a))

        def do_GET(self):
            if self.path.startswith(PROXY):
                return self.proxy_library(self.path[len(PROXY):])
            if self.path == "/walkthrough-overlay.js":
                body = OVERLAY_JS.encode("utf-8")
                self.send_response(200); self.send_header("Content-Type", "application/javascript; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            if self.path.split("?")[0] in ("/ac-dc-app/index.html", "/ac-dc-app/"):
                # the app's page with the overlay script appended — the file in the submodule is not changed
                html = (SUB / "ac-dc-app" / "index.html").read_text(encoding="utf-8")
                tag = '<script src="/walkthrough-overlay.js"></script>'
                html = html.replace("</body>", tag + "\n</body>") if "</body>" in html else html + tag
                body = html.encode("utf-8")
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            if self.path.rstrip("/") in ("/walkthrough", "/walkthrough.html"):
                body = walkthrough_page(port)
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            if self.path.startswith("/media/"):
                # docs/walkthrough.md links its recording as media/<file>, relative to docs/. The server's root is
                # the submodule, which has no media/, so the link answered 404 (LG's run, 2026-10-01). Served from
                # docs/media and nowhere else: a path that resolves outside that directory is refused.
                import mimetypes
                import urllib.parse
                media = (ROOT / "docs" / "media").resolve()
                f = (media / urllib.parse.unquote(self.path.split("?")[0][len("/media/"):])).resolve()
                if f.parent != media or not f.is_file():
                    return self.send_error(404, "File not found")
                body = f.read_bytes()
                self.send_response(200); self.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "application/octet-stream"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            return super().do_GET()

        def proxy_library(self, rest: str):
            """GET LIBRARY + rest with the api-key header; relay status, content type and body."""
            import urllib.request, urllib.error
            if not API_KEY:
                body = b'{"error": "CDISC_API_KEY is not set in the environment of walkthrough.py serve"}'
                self.send_response(401); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            rest = rest.split("?")[0]
            req = urllib.request.Request(LIBRARY + rest, headers={"api-key": API_KEY, "Accept": "application/json", "User-Agent": "usdm-acdc-in-practice walkthrough"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    body = r.read(); status = r.status; ctype = r.headers.get("Content-Type", "application/json")
            except urllib.error.HTTPError as e:
                body = e.read(); status = e.code; ctype = e.headers.get("Content-Type", "application/json")
            except (urllib.error.URLError, OSError) as e:
                body = json.dumps({"error": f"could not reach the CDISC Library: {e}"}).encode("utf-8"); status = 502; ctype = "application/json"
            wants_page = "text/html" in (self.headers.get("Accept") or "") and "raw=1" not in self.path
            if status == 200 and wants_page:
                try:
                    body = render_library_html(json.loads(body.decode("utf-8")), rest); ctype = "text/html; charset=utf-8"
                except (ValueError, TypeError):
                    pass  # not JSON after all: relay as received
            self.send_response(status); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    NoCache.extensions_map.update({".js": "application/javascript", ".json": "application/json", ".css": "text/css", ".svg": "image/svg+xml"})
    http.server.ThreadingHTTPServer.request_queue_size = 64
    httpd = http.server.ThreadingHTTPServer(("", port), functools.partial(NoCache, directory=str(SUB)))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        say("\nstopping")
    finally:
        httpd.server_close()
        clean()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["stage", "serve", "clean", "html"])
    ap.add_argument("--out", default=None, help="html: where to write the standalone page (default: your temp directory)")
    ap.add_argument("--port", type=int, default=8080, help="serve: port (default 8080)")
    ap.add_argument("--toriva", default=None, help="path to the TORIVA-LUNG 301 checkout")
    args = ap.parse_args()
    {"stage": stage, "serve": serve, "clean": clean, "html": html}[args.command](args)


if __name__ == "__main__":
    main()
