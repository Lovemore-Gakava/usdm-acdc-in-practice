# Lab change from baseline — comparison against built ADaM

Step 3 of the method. **The first time in this repository that any claim has been checked
against data rather than against a specification.**

Ground truth: TORIVA-LUNG 301 at `8534339d`, `datasets/adam/adlb.parquet` — 136,242 rows,
37 columns, 5,400 subject × parameter groups. Read with `pyarrow` 25.0.1.

---

## What is and is not being compared

**Scope limit, stated first.** The chain in [`chain.json`](chain.json) was authored against the
**CDISC Pilot** study, because that is the only study the shipped builder carries; TORIVA USDM
fragments do not exist (specification §15.3, still open). So this is **not** a numeric diff of
the authored chain's output against TORIVA's columns.

What it is: a test of whether **the definition the concept model is able to express** reproduces
the definition TORIVA built. That is the question step 3 exists to answer — *"either the model
cannot express something real, or it has exposed an ambiguity the SAP was carrying silently"* —
and it can be answered without the two studies matching, because the derivation is the same
derivation.

---

## Divergence 1 — the model cannot say *which* baseline record. **Model limitation.**

This is [F12](../../docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md),
and the data settles it.

The model reaches the baseline value only through `T.ChangeFromBaseline`'s slice:

```
parameter_baseline:  Parameter = {parameter}   AND   AnalysisVisit = {baseline_visit}
```

TORIVA reaches it through `ABLFL` — the last non-missing record on or before `TRTSDT`.

The two agree on *which visit*. They disagree on *how many records that identifies*:

| | |
|---|---|
| Subject × parameter groups | 5,400 |
| Groups where `ABLFL='Y'` is **not** at `AVISIT='Baseline'` | **0** |
| Groups where `BASE` ≠ `AVAL` of the `ABLFL` record | **0** |
| **Groups carrying *two* rows at `AVISIT='Baseline'`** | **3,832 (71%)** |
| Groups carrying one | 1,537 |
| Groups carrying none | 31 |

The 3,832 are every subject × parameter whose screening draw and Cycle 1 Day 1 pre-dose draw
both window into the baseline visit — collected `VISIT` pairs are `('C1D1', 'SCREENING')` in
**all 3,832 cases**.

So `AnalysisVisit = Baseline` is not a key. It selects two records for 71% of the study, and
the model has no way to choose between them.

### It matters numerically, not just formally

The two candidate records carry **different values in 3,710 of 3,832 groups (96.8%)**. Had the
other been taken as `BASE`:

| | median | mean | p90 | max |
|---|---|---|---|---|
| \|relative difference\| in `BASE` | **21.3%** | 46.5% | 87.0% | 2750% |

`CHG` is `AVAL − BASE`, so that error passes straight through to every change-from-baseline
value for that subject and parameter.

### What disambiguates them is a flag the model cannot reach

Exactly one of the two rows carries `ABLFL='Y'`, and exactly one carries `ANL01FL='Y'` — and
they are **the same row in all 3,832 groups**, which is SAP §12.2's rule (*"inside the
`Baseline` visit the `ABLFL='Y'` record wins"*) holding in the built data.

Both of those flags are outside what the chain can use:

- `ABLFL` **is** derivable — `T.BaselineSelection` produces it — but its output is a `Flag`, so
  it can never resolve a `Measure` dependency and the slice cannot reference it
  ([F12](../../docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md)).
- `ANL01FL` has no transformation at all
  ([F11](../../docs/findings/F11-analysis-record-flag-has-no-transformation.md)).

**So F11 and F12 compose into a single concrete failure**: the one piece of information that
makes `BASE` well-defined is derived by the framework and unusable by it, or not derivable at
all. This is the simplest derivation in the library, on a study where everything else matched.

### Why TORIVA does not hit this

`adlb.R` calls `apply_baseline_visit()`, which forces `AVISIT="Baseline"` onto the `ABLFL='Y'`
record. That is what makes flag and visit agree — and it is a *labelling* step, not a
selection step. It does not reduce the two Baseline rows to one; `ANL01FL` does that. Nothing
in the concept model corresponds to either.

---

## Divergence 2 — `ANRIND` and `BNRIND` do not exist. **Specification error. D8 confirmed.**

`ADLB-spec.md` lists #24 `BNRIND` and #25 `ANRIND` as derived L/N/H from `AVAL`/`BASE` against
`ANRLO`/`ANRHI`. The built dataset carries neither:

```
ANRIND present: False
BNRIND present: False
NRIND  present: True
```

`NRIND` is the SDTM predecessor renamed (`adlb.R:53`, `NRIND = LBNRIND`). The spec describes a
derivation; the code performs a rename. D8 is confirmed **against the data**, not just against
the spec, and closed.

Relevant to this project: had the spec's derivation been implemented, it would have needed a
predicate over a value and two per-record bounds — [F06](../../docs/findings/F06-no-general-predicate.md).

## Divergence 3 — `BTOXGR` does not exist. **Specification error. D9 confirmed.**

`ADLB-spec.md` #27 lists it and the T-LB-02 cross-reference names it. The data carries
`ATOXGR` and `ATOXGRN` and no baseline toxicity grade. Confirmed and closed.

## Non-divergence — the parts that agree

Recorded because a comparison that only lists failures is not a comparison.

| Check | Result |
|---|---|
| Record count vs `ADLB-spec.md` header (136,242) | **exact** |
| `CHG = AVAL − BASE` | holds on **135,421 / 135,421** rows carrying `CHG` |
| `BASE` = `AVAL` of the `ABLFL` record | holds on all 5,357 groups with a baseline |
| Groups with >1 `ABLFL='Y'` (P21 AD0154) | **0** |
| Groups with no `ABLFL` | 43 — consistent with SAP §12.3's retained-but-excluded rule |
| `ABLFL` and `ANL01FL` agreeing inside the baseline visit | **3,832 / 3,832** |

TORIVA's ADLB is internally consistent on every rule its SAP states. The divergence is not
between the SAP and the code; it is between the SAP and **what the concept model can say**.

---

## Classification

| # | Divergence | Class |
|---|---|---|
| 1 | Baseline record not identifiable — `AnalysisVisit = Baseline` selects two rows in 71% of groups, differing in value 96.8% of the time | **Model limitation** (F11 + F12) |
| 2 | `ANRIND` / `BNRIND` specified, not built | **Specification error** (D8) |
| 3 | `BTOXGR` specified, not built | **Specification error** (D9) |

No authoring errors: the chain resolved without an unresolved slot, and every binding the
builder demanded was satisfiable.

## What this changes

The lab tier's paper mapping called Chain A steps 5 and 6 a clean compose. At the level of
*structure* that holds — the chain authors, validates and serialises. At the level of
*semantics* it does not: the chain as authored would compute a different `BASE` from TORIVA's
for most of the study, and nothing in the artefact records that it is under-determined.

That is the sharpest available answer to the specification's own question — *"if we adopted
this, what would actually happen?"* On the simplest endpoint in the ladder, what would happen is
a chain that looks complete, passes the builder, and is wrong by a median 21% on the baseline
it subtracts.

## Reproduce

```
pip install pyarrow
git -C <toriva> sparse-checkout add /datasets/adam/adlb.parquet
python tools/check_baseline_ambiguity.py --adlb <toriva>/datasets/adam/adlb.parquet
```
