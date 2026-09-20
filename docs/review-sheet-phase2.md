# Review sheet — phase 2, for LG

Written 2026-09-19, the day phase 2 completed. You have read none of it. This sheet lists the
claims phase 2 rests on, each stated so it can be disagreed with, and what would falsify each.
Where a falsifier is mechanical it has already been run and the result is given; what remains
is the judgement only you can make. Record verdicts at the bottom — *holds / narrower than
stated / wrong* — and put "how much narrower" in the source file, not here.

The selection rule: a claim is on this sheet if being wrong about it would make a phase-2 stage
green that should not be. Nothing here asks whether the framework is adequate.

---

## 1. The register's dispositions — `study/gap-register.md`

> **The claim.** Every gap has the right disposition under your rule: *fix here* only where the
> derived work can carry a correction, *sponsor decision* where inventing would make the
> document conformant and untrue, *upstream only* where the defect is in TORIVA's programs or
> data.

**Yours by definition:** the five **sponsor decision** rows (D11, G2, G5, G6, G7 — *"seven"*
until 2026-09-20, a miscount corrected in place). Each says the source does not contain the information. If you know that any of
it *does* exist somewhere in TORIVA's document set, the row is wrong and the P1 section that
records it "absent" is wrong with it.

| Falsifier | Status |
|---|---|
| 1a — a *fix here* row has no check in `check_alignment.py` | mechanical; the tool fails on it; **0 such rows** |
| 1b — an *upstream only* row is actually fixable in a derived protocol (e.g. D1's `RANDDT` vs `TRTSDT` origin could be *stated* in §10 even if the data disagrees) | judgement — yours |
| 1c — X4 (the two-rows-at-Baseline situation) is a study gap after all, because a protocol should have said which draw is baseline | judgement — yours; the register says SAP §12.3 specifies it and the data follows |

## 2. P1 — the move is verbatim and the sections are the right sections

> **The claim.** Every block in the eleven generated sections is an unchanged line range of the
> synopsis at `8534339d`, and each range sits under the M11 section it belongs to.

| Falsifier | Status |
|---|---|
| 2a — a moved block differs from the source | mechanical: `python tools/m11_restructure.py --synopsis <path> --check` → **OK**, all 13 files |
| 2b — a source section is assigned to the wrong M11 section (e.g. §10 *Key Information for CRF Design* placed under M11 §11 Data Handling; §11 *Key Information for the SAP* placed under §10.1 General Considerations; §5.3 dose modifications placed under §7 Discontinuation) | judgement — yours; the map is `SECTIONS` in `tools/m11_restructure.py`, one screen |
| 2c — an "absent" note is wrong because the content is elsewhere in the synopsis | judgement; the notes say where content was found when it was; **41 absent-element notes** across the eleven sections |
| 2d — M11 section titles: the generator's titles were taken from the element pages' subsections, not from a section index (the index page did not parse). §7's and §9's long titles are my reconstruction | mechanical to check against the M11 template's table of contents — **not done**; low stakes, but say if a title is wrong |

## 3. P2 — the generated USDM says what the protocol says, corrected only where the data overrules it

> **The claim.** Arms, interventions, epochs, encounters, activities and the schedule are
> derived from the M11 sections; the only departures from the source are D14 and D15, applied
> because the built data is the ground truth, and each carries the source's wording in `notes`.

| Falsifier | Status |
|---|---|
| 3a — "the data is the ground truth" is the wrong rule: a derived *protocol* should say what the protocol says, and the data should be the thing flagged | **judgement — yours, and the most consequential one on the sheet.** If you reverse it, the arms revert to monotherapy and 2:1 in the USDM, and P3's data checks become WARNs instead of PASSes |
| 3b — the schedule rules are misread. My arithmetic: *C3, C5, then Q6 cycles* → cycles 3, 5, 11, 17, 23, 29, 35; *C3, C5, then Q12 weeks* → 3, 5, 9, 13 … (12 weeks = 4 cycles); *Q6 weeks (FOCBP)* → every second cycle from 3; imaging *Q6W for 12 months, Q12W after* → every second cycle to 17, every fourth from 21 | judgement — yours; the rules are `cycles_for_rule` and `tumour_cycles` in `tools/m11_to_usdm.py`, twenty lines |
| 3c — "Cycle 7+ = maintenance" is a data convention the protocol never states; the generator names encounters `C7D1…C35D1` while the data says `MAINT_C1D1…` | mechanical: `check_alignment.py` reports it as **INFO** (SoA↔AVISIT); whether the *protocol* should adopt the SAP's names is yours |
| 3d — the chemotherapy backbone as a third `StudyIntervention` invents a protocol element from a SAP sentence | judgement — yours; it is marked as SAP-sourced |
| 3e — the fragment fails to load in the app | mechanical: loaded 2026-09-19, arms/BCs/endpoints/schedule rendered — **holds** |

## 4. P3 — the alignment tool tests what it says it tests

> **The claim.** `check_alignment.py` verifies every fix-here promise in the files named, and
> its five WARNs are the known upstream divergences, confirmed against the data.

| Falsifier | Status |
|---|---|
| 4a — a PASS is vacuous (e.g. D13 passes on the string "risk difference" appearing anywhere in the §3.2.2 block) | judgement; read `study/alignment-report.md` once — 24 rows |
| 4b — the endpoint-text check compares only the first 70 normalised characters | mechanical fact; a later divergence in an endpoint's wording would pass. **Narrower than the claim**, recorded here |
| 4c — the data layer is silently skipped on a machine without TORIVA | mechanical: it reports **SKIP**, and P3 still goes green on documents alone — by design; say if you want the data layer required |

## 5. The M.MMRM implementation's three rules — `endpoints/04-vitals-cfb-mmrm/r_impl_mmrm.json`

> **The claim.** The three rules written into the implementation are what any MMRM on this
> engine's cube needs and none of them changes what the analysis means.

| Falsifier | Status |
|---|---|
| 5a — keeping the *first* row per subject × visit is not neutral: it is the engine's convention, but a statistician would take the `ANL01FL` row | **judgement — yours.** The reference did the same, so the comparison is fair; the *analysis* is still one a statistician would not sign |
| 5b — dropping "the visit at which every change is zero" could drop a real visit in another dataset (any visit where every subject's change is exactly zero) | judgement; true in principle, impossible on continuous data in practice; recorded |
| 5c — the induction-visit window (V-D14) is a modelling decision the SAP never made and should not sit in a data-preparation step | judgement — yours |
| 5d — the implementation reproduces local `mmrm` | mechanical: **identical at all six visits and the AIC** |

## 6. P5 — "identical" means what it should

> **The claim.** Re-running on the generated fragment gave the same numbers because the
> selection was the same; the arms renaming, the schedule and the endpoint texts do not enter
> the execution.

| Falsifier | Status |
|---|---|
| 6a — the re-runs reused the old chains, so they could not have picked up any change | **true, and intended**: P5 asks whether the *study description* changing altered the number — it did not, because the chain binds by endpoint id and dimension value, and `TRT01P` came from the data both times. If you wanted the chains *re-authored* on the new fragment, that is a different stage |

---

## Verdicts

| Item | Verdict | Date | Notes |
|---|---|---|---|
| 1 — dispositions (1a–1c) | **wrong, and the rule with it** | 2026-09-20 | LG: the gaps are corrected *here*, and *"the documents are what get corrected"* — the data follows, later, upstream. Six decisions → P6. 1c: X4 stays excluded; the baseline-selection rule belongs to the SAP |
| 2 — the move (2a–2d) | | | |
| 3 — the USDM (3a–3e) | 3a **wrong** — reversed; 3b–3e open | 2026-09-20 | the fragment regenerated under P6: arms per the corrected protocol, 2:1; data checks D14/D15 → WARN on divergence |
| 4 — the alignment tool (4a–4c) | | | |
| 5 — the MMRM rules (5a–5d) | | | |
| 6 — P5's meaning (6a) | | | |

The one that changes the most if you disagree is **3a**. Everything else is local.
