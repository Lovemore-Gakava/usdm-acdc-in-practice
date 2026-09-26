# Troubleshooting and environment facts

Read when something breaks, not before. Split out of `CLAUDE.md` on 2026-09-26, which had
become a workaround register pretending to be onboarding instructions.

Each of these cost real time once. Several have since been **converted into code**, which is
the preferred fate — a guard that fires beats a sentence someone has to have read. Where that
has happened it is noted, and the entry stays as the explanation of *why* the code exists.

---

## Set-up

Run `tools/bootstrap.py` with whatever Python the machine has: `python` or `py -3` on LG's
Windows machine, `python3` on macOS, where there is no `python` at all. **Never assume the
name.** It does the submodule, the hook, `.venv` and TORIVA at the pin, then runs
`check_alignment.py` to prove P3. Idempotent; `--check` reports without changing anything.

**Afterwards, anything that reads parquet needs `.venv`'s interpreter** — `.venv/bin/python`,
`.venv\Scripts\python.exe` on Windows. *Now code:* `tools/_deps.py` prints the exact command
when an import fails, because this rule was written down and still caught the person who wrote
it, an hour later.

The pre-commit hook prefers `.venv` automatically. Without that it scored P3, P6 and P7 red on
a clone that had everything, because `check_alignment.py --require-data` could not import
`pyarrow`.

Note that running `check_alignment.py` on an interpreter without `pyarrow` **rewrites
`study/alignment-report.md` without the data layer** — 27 checks rather than 37. Regenerate it
with `.venv` before committing.

## The submodule

`upstream/analysis-concepts` is a **pinned, read-only submodule** at `739344c`. Never edit it;
if a local change is unavoidable, `git -C upstream/analysis-concepts checkout <path>` after.

It shows `HEAD detached at 739344c` **by design** — a submodule is a pinned commit, not a
branch. Do not put it on a branch. `739344c` was the tip of upstream `main` as of 2026-09-20.
When upstream moves, re-pin deliberately: update the hash in the parent, re-run
`tools/check_consistency.py`, and record what changed (LG, 2026-09-20).

## TORIVA

**Referenced, never vendored.** Recipe and pin in `study/source-refs.md`; `bootstrap.py` is the
supported route. `/datasets/adam/` is required, not optional — `find_toriva()` tests for
`datasets/adam/adsl.parquet` and refuses a checkout without it.

On Git Bash for Windows, prefix `sparse-checkout set` with `MSYS_NO_PATHCONV=1` or it silently
yields an empty working tree with no error. *Now code:* `bootstrap.py` sets it.

`pyarrow.dataset` is blocked by Application Control on **LG's Windows machine** — use
`pq.ParquetFile(...).read()`, not `pq.read_table`.

## Running the app

Use `tools/walkthrough.py serve`, **not** upstream's `serve.py`: upstream's is single-threaded
with a backlog of five and drops some of the app's ~22 parallel fetches on Windows, and the page
then says *Failed to load data*.

`walkthrough.py serve` stages the study, chains, implementation and `.xpt` data into the app,
serves it threaded, and cleans the submodule on Ctrl-C (`stage` / `clean` separately). It
refuses to stage over foreign changes in the submodule, and refuses to finish `clean` while
`git status` there is not empty.

It also serves `docs/walkthrough.md` at `/walkthrough` (own renderer, no Markdown package
needed; `walkthrough.py html` writes the same page to a file), proxies the CDISC Library at
`/cdisc-library/` with the key from `.cdisc-api-key` or `CDISC_API_KEY`, and injects an
**overlay script** into the page at serve time — a *(no filter)* entry in every slice dropdown,
`M.MMRM` registered, `mmrm` installed once WebR is up — so the walkthrough needs no console
steps. The submodule's files are not changed; the guide says at each step what the overlay
supplied.

Without a Library key, concept Reference links answer 401.

## Step 8 (WebR)

**It will not parse the engine with CRLF endings.** `core.autocrlf=true` checks
`ac-dc-app/r/acdc_engine.R` out as CRLF and R reports `unexpected invalid token`. Fix once per
clone: `git -C upstream/analysis-concepts config core.autocrlf false`, then re-checkout the
file. The submodule stays clean.

Step 8 also needs `.xpt`; TORIVA is parquet — `pyreadstat.write_xport`, which `walkthrough.py`
does at stage time.

## Browser automation

The builder's **Load** button opens a native file picker and can call `alert()`; both freeze
browser automation. Call `deserializeStudyInstance` on `window.appState` instead:

```js
const ser = await import('/ac-dc-app/js/utils/instance-serializer.js');
ser.deserializeStudyInstance(await (await fetch('/ac-dc-app/data/toriva/lab-chain.json')).json(), window.appState);
```

## Method implementations are pluggable at runtime

The app reads `lib/method_implementations/r_implementations.json` into
`appState.methodImplementationCatalog`; an entry added there **in the page** (same shape as
`M.ANCOVA`'s) executes without touching the submodule. WebR can `webr::install("mmrm")`.

`endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json` is the worked example, with the three rules an
MMRM needed that the engine's data layer did not give it. This is how stage 6 was reached for
the vitals endpoint after `No R implementation available for M.MMRM`.
