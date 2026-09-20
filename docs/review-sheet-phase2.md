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
| 2b — a source section is assigned to the wrong M11 section (e.g. §10 *Key Information for CRF Design* placed under M11 §11 Data Handling; §11 *Key Information for the SAP* placed under §10.1 General Considerations; §5.3 dose modifications placed under §7 Discontinuation) | judgement — yours; the map is `SECTIONS` in `tools/m11_restructure.py`, one screen. **The 2d run sharpened this**: M11's own numbering puts four of the moved blocks in a different section from where they sit — randomisation and blinding (§3.3, §3.4) under **6.7**, not 4.1; dose modifications and treatment delays (§5.3, §5.3.1) under **6.4**, not 7.1; the myocarditis stopping rule (§7.4) under **4.3**, not 7; the Safety Monitoring Committee (§7.5) under **11.4 Committees**, not 9. **LG, 2026-09-20: moved to where M11 numbers them** (generator `SECTIONS` map; text unchanged, `--check` OK). The other three placements (CRF design at 11.7, SAP-information table at 10.1, irAE management at 9.4) stand as labelled |
| 2c — an "absent" note is wrong because the content is elsewhere in the synopsis | **Run 2026-09-20 against the whole TORIVA checkout** (synopsis, SAP, CRF strategy, programming specs, programs; data files excluded), a term search per absent element. **One note wrong**: 6.7.4 emergency unblinding, which is inside the §3.4 text — written that morning and corrected the same day. **Three narrower**: drug accountability (6.6.3), the screening visit's window and procedure list (8.2) and the baseline biomarker panel (8.6) exist in TORIVA's CRF strategy and specs, not in the protocol; the notes now say so. Two minor (adherence via the DA form; major-deviation categories in the SAP). The rest hold: no approval date, design rationale, post-trial access, lifestyle restrictions, rescreening, overdose, loss-to-follow-up management, pregnancy reporting, product complaints, oversight, insurance, RBQM, source records, site closure or dissemination anywhere in the document set |
| 2d — M11 section titles: the generator's titles were taken from the element pages' subsections, not from a section index (the index page did not parse). §7's and §9's long titles are my reconstruction | **Run 2026-09-20 — narrower than stated.** The *section* titles were right; the *subsection* labels were not: eight of 43 were numbered wrong against the 132 subsection numbers in the element pages (Sample Size 10.9 → 10.11, Interim 10.8 → 10.9, Primary Analysis 10.3 → 10.4, Secondary 10.4 → 10.5, Data Protection 11.4 → 11.8, CRF design 11.5 → 11.7, Concomitant Therapy 6.8 → 6.10, AESI 9.6 → 9.2.4), and the per-section element lists in the generator were reconstructed from memory with the same errors. All corrected in `tools/m11_restructure.py` and regenerated; the moved text is unchanged. Four blocks sit in a section M11 does not put them in — see 2b |

## 3. P2 — the generated USDM says what the protocol says, corrected only where the data overrules it

> **The claim.** Arms, interventions, epochs, encounters, activities and the schedule are
> derived from the M11 sections; the only departures from the source are D14 and D15, applied
> because the built data is the ground truth, and each carries the source's wording in `notes`.

| Falsifier | Status |
|---|---|
| 3a — "the data is the ground truth" is the wrong rule: a derived *protocol* should say what the protocol says, and the data should be the thing flagged | **judgement — yours, and the most consequential one on the sheet.** If you reverse it, the arms revert to monotherapy and 2:1 in the USDM, and P3's data checks become WARNs instead of PASSes |
| 3b — the schedule rules are misread. My arithmetic: *C3, C5, then Q6 cycles* → cycles 3, 5, 11, 17, 23, 29, 35; *C3, C5, then Q12 weeks* → 3, 5, 9, 13 … (12 weeks = 4 cycles); *Q6 weeks (FOCBP)* → every second cycle from 3; imaging *Q6W for 12 months, Q12W after* → every second cycle to 17, every fourth from 21 | **Laid beside the source and the data, 2026-09-20.** The arithmetic follows the §6.1 and §7.2 cells as written — holds as a reading. The *data* reads two cells differently: imaging is 6-weekly throughout to week 120 (**D16**, new) and every subject has a Cycle 1 Day 15 visit the protocol never schedules (**D17**, new). Both are upstream-only under P6's rule and WARN in the alignment report. The one judgement — whether *"Q6 cycles"* means every sixth cycle after C5 or every six weeks — **LG, 2026-09-20: every sixth cycle**, which is what the generator does (11, 17, 23, 29, 35) |
| 3c — "Cycle 7+ = maintenance" is a data convention the protocol never states; the generator names encounters `C7D1…C35D1` while the data says `MAINT_C1D1…` | **Decided by P6's rule, 2026-09-20: the protocol's names stand.** The alignment tool now translates `MAINT_CnD1` to cycle n+6 before comparing, so the INFO row says what really fails to match instead of everything |
| 3d — the chemotherapy backbone as a third `StudyIntervention` invents a protocol element from a SAP sentence | **Holds under P6, 2026-09-20.** The corrected protocol states the combination (title page, §3.0), so the backbone is the corrected protocol's background intervention (M11 6.9.1), no longer a SAP sentence; the intervention's description says so |
| 3e — the fragment fails to load in the app | mechanical: loaded 2026-09-19 and again 2026-09-20 on the P6-regenerated fragment (the design note the app loaded is recorded in each `results.json`) — **holds** |

## 4. P3 — the alignment tool tests what it says it tests

> **The claim.** `check_alignment.py` verifies every fix-here promise in the files named, and
> its five WARNs are the known upstream divergences, confirmed against the data.

| Falsifier | Status |
|---|---|
| 4a — a PASS is vacuous (e.g. D13 passes on the string "risk difference" appearing anywhere in the §3.2.2 block) | **Run 2026-09-20 as a mutation test**, `tools/mutate_alignment.py`: sixteen corruptions of the things the documents-layer checks claim to verify, each run against the tool in a scratch copy. First pass: four survived. Two were weak mutations. Two were weak checks, exactly as the falsifier predicted — **G4** counted the three-letter code as a bare substring ("ALP" is inside "ALPHA"), **G7/D11** matched the word *shift* anywhere in §3.2.5. D13 was tightened to the Population-level Summary row itself and G3 to the conformance row before the test ran. After tightening: **16 of 16 caught**. The test is kept in `tools/` and exits 1 if any survive |
| 4b — the endpoint-text check compares only the first 70 normalised characters | **Fixed 2026-09-20**: the whole normalised text is compared; all seven endpoints match whole (35 to 263 characters), and the mutation test appends a word to END-OS and sees it fail |
| 4c — the data layer is silently skipped on a machine without TORIVA | mechanical: it reports **SKIP**, and P3 still goes green on documents alone — by design. **Recommendation, 2026-09-20, yours to take:** P3 says *alignment verified*, and half of alignment is the built ADaM; a P3 that is green without the data layer having run overstates. Make the checker require the data layer for P3 (`--require-data`), so on a clone without TORIVA the row is red and the report says why. The trade: the scoreboard is only fully green where TORIVA is checked out. **LG, 2026-09-20: changed.** `--require-data` added; the checker passes it for P3; the report header says when alignment is not verified |

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
| 2 — the move (2a–2d) | 2a holds; 2d **narrower than stated**, corrected; 2b **four blocks moved** on LG's verdict; 2c **run**: one note wrong, three narrower, corrected | 2026-09-20 | eight subsection numbers were wrong and the per-section element lists with them; M11's numbering then showed four blocks in the wrong section; the whole-checkout search then found one absent-note wrong and three narrower. **Item 2 closed** |
| 3 — the USDM (3a–3e) | 3a **wrong**, reversed; 3b holds as a reading, two data divergences found (D16, D17); 3c decided by P6; 3d, 3e hold | 2026-09-20 | *"Q6 cycles"* = every sixth cycle (LG). **Item 3 closed** |
| 4 — the alignment tool (4a–4c) | 4a **two vacuous checks found and tightened**, 16/16 mutations now caught; 4b fixed; 4c **changed** (LG): P3 requires the data layer. **Item 4 closed** | 2026-09-20 | the falsifier's own example, D13, was a real weakness; the mutation test is now a tool |
| 5 — the MMRM rules (5a–5d) | | | |
| 6 — P5's meaning (6a) | | | |

The one that changes the most if you disagree is **3a**. Everything else is local.
