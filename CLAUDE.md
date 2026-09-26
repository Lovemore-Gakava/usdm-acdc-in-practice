# CLAUDE.md

**Read [`NORTH.md`](NORTH.md) before doing anything else.** It states the destination, the
nine-stage finish line, and the test every piece of work must pass. This file says how to work;
`NORTH.md` says what for.

## The test

Before starting any piece of work, answer:

> **Which numbered stage of `NORTH.md`'s finish line does this advance?**

No number → do not do it. Say so and propose the work that does carry a number.

This applies to work you propose *and* to work you are asked for. If a request has no stage
number, say which stage it displaces before starting — the user may still want it, but the
trade should be visible rather than silent.

## Do not drift

The project drifted once, badly, and the mechanism is worth knowing because it will recur.

Findings about what the framework *cannot* do are cheap to produce, feel like progress, and
advance no stage. There are already thirteen. **Do not add another unless it blocks a stage you
are actively trying to complete**, and when one does, record it in two paragraphs and move on.

**The upstream issues and the review plan are parked** — `docs/findings/upstream-issues.md`,
`docs/review-plan.md`. Do not polish them, do not propose filing them, and do not treat the
review backlog as a blocker. Nothing is being filed against `cdisc-org/analysis-concepts` — with one decided exception: the `M.MMRM`
implementation is *prepared* for upstream in `docs/contribution-mmrm.md` (LG, 2026-09-19), and
only LG files it. Preparing it is not a licence to prepare anything else.

TORIVA is different: it is LG's own project. On 2026-09-20 LG had the seventeen discrepancies and the
documents-first rule filed there as one issue (`OpenTrialReporting/torivumab-nsclc-301#27`), on LG's
explicit yes to a draft shown first. That is the pattern for anything outward-facing: draft, show, wait.

**The SAP is an input, not a yardstick.** `study/usdm/README.md` fixes the layering: protocol +
CDISC Library → USDM, SAP → DC/AC. So the SAP tells you *what derivation to author*. The moment
it is used the other way round — *here is what the SAP says, here is what the model cannot say* —
the work has become an assessment of `cdisc-org/analysis-concepts` again, whatever it is called.
This is the drift's second shape and it is harder to see than the first, because every individual
step is legitimate. It recurred on 2026-09-17, inside an hour of the README being restructured to
remove it, and LG caught it, not the model.

The check: **what does this comparison decide?** If the answer is *whether the framework is
adequate*, stop. If it is *whether I authored the chain correctly*, continue.

Specific failures to avoid, each of which actually happened here:

- Noticing drift and continuing. Writing *"I should stop generating findings"* and then
  generating two more. **If you notice drift, stop and ask.**
- Treating a request for one more artefact as licence to skip the test.
- Producing rigour where it is not needed — three corrections to a finding nobody asked for,
  while stages 1, 2, 5 and 6 sat untouched.

## Verification discipline

This is the part of the old process worth keeping. Five findings have had a premise or fix
disproved, so:

- A claim about the **libraries** cites a path and `$defs` name at the pinned commit, or a count
  reproducible by a command in the file.
- A claim about **history** uses `git log -S` — it distinguishes *removed* from *never present*.
- A claim about the **application** is not established until the app has been **run**. Three
  findings went wrong by inferring behaviour from library JSON. Serve it:
  `python tools/walkthrough.py serve` from the repository root, then
  `http://localhost:8080/ac-dc-app/index.html` (not upstream's `serve.py` — see the repository facts:
  it drops some of the app's parallel fetches on Windows and the page says *Failed to load data*).
- A claim about **TORIVA's data** needs the parquet read, not its markdown specification.

## Repository facts

- `upstream/analysis-concepts` is a **pinned, read-only submodule** at `739344c`. Never edit it;
  if a local change is unavoidable, `git -C upstream/analysis-concepts checkout <path>` after.
  It shows `HEAD detached at 739344c` by design — a submodule is a pinned commit, not a branch — and
  `739344c` is the tip of upstream `main` as of 2026-09-20. Do not put it on a branch. When upstream
  moves, re-pin deliberately: update the hash in the parent, re-run `tools/check_consistency.py`,
  and record what changed (LG, 2026-09-20).
- TORIVA-LUNG 301 is **referenced, never vendored**. Sparse-checkout recipe in
  `study/source-refs.md`. On Git Bash for Windows, prefix `sparse-checkout set` with
  `MSYS_NO_PATHCONV=1` or it silently yields an empty tree.
- `tools/check_consistency.py` runs on every commit via `.githooks/pre-commit`. It verifies that
  documents match the filesystem **and** that `NORTH.md`'s status table is true. Enable the hook
  once per clone: `git config core.hooksPath .githooks`.
- `tools/check_baseline_ambiguity.py` needs `pyarrow`, declared with the other data dependencies
  in `requirements.txt`. Note `pyarrow.dataset` is blocked by Application Control on **LG's
  Windows machine** — use `pq.ParquetFile(...).read()`, not `pq.read_table`.
- **Set-up is `python tools/bootstrap.py`** — submodule, hook, `.venv`, TORIVA at the pin, then
  it runs `check_alignment.py` to prove P3. Idempotent; `--check` reports without changing.
  Anything that reads parquet needs the virtual environment's interpreter
  (`.venv/bin/python`, `.venv\Scripts\python.exe` on Windows), not the system one.
- The interpreter's name is **machine-specific**: `python` on LG's Windows machine, `python3` on
  macOS (there is no `python` there at all). `bootstrap.py` runs under either.
- **Step 8 (WebR) will not parse the engine with CRLF endings.** `core.autocrlf=true` checks
  `ac-dc-app/r/acdc_engine.R` out as CRLF and R reports `unexpected invalid token`. Fix once per
  clone: `git -C upstream/analysis-concepts config core.autocrlf false`, then re-checkout the file.
  The submodule stays clean. Step 8 also needs `.xpt`; TORIVA is parquet — `pyreadstat.write_xport`.
- **Method implementations are pluggable at runtime.** The app reads
  `lib/method_implementations/r_implementations.json` into `appState.methodImplementationCatalog`;
  an entry added there in the page (same shape as `M.ANCOVA`'s) executes without touching the
  submodule. WebR can `webr::install("mmrm")`. `endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json` is
  the worked example, with the three rules an MMRM needed that the engine's data layer did not give it.
- The builder's **Load** button opens a native file picker and can call `alert()`; both freeze
  browser automation. Call `deserializeStudyInstance` on `window.appState` instead.
- `python tools/walkthrough.py serve` stages the study, chains, implementation and `.xpt` data into
  the app, serves it with a **threading** server (upstream's `serve.py` is single-threaded with a
  backlog of five and drops some of the app's ~22 parallel fetches on Windows — the page then says
  *Failed to load data*), and cleans the submodule on Ctrl-C (`stage` / `clean` separately). It refuses
  to stage over foreign changes in the submodule and refuses to finish `clean` while `git status`
  there is not empty. It also serves `docs/walkthrough.md` as a page at `/walkthrough` (own renderer, no
  Markdown package needed; `walkthrough.py html` writes the same page to a file), proxies the CDISC
  Library at `/cdisc-library/` with the key from `.cdisc-api-key` or `CDISC_API_KEY`, and injects an
  **overlay script** into the app's page at serve time — a *(no filter)* entry in every slice dropdown,
  the M.MMRM implementation registered, `mmrm` installed once WebR is up — so the walkthrough needs no
  console steps. The submodule's files are not changed; the guide says at each step what the overlay
  supplied.

## Writing

Match the existing voice: direct, evidence-first, corrections left visible rather than deleted.
When something turns out wrong, amend it in place and say what changed — the repository's
record of its own errors is one of the few things in it worth keeping.

Do not restate a finding's full argument in the README, the finding file, `PROVENANCE.md` and a
commit message. Say it once, in the finding, and link.
