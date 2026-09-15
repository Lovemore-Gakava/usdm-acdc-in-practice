# Concept Spine — Specification and Plan

**Part A: a flow snapshot demonstrating protocol → USDM → BC/DC/AC on real endpoints.
Part B: a governance and traceability overlay on the CDISC AC/DC framework.**

Status: draft for review
Version: 0.3 — Part A is new and is the near-term work. Part B is unchanged in substance but deferred. See §17 for what changed and why.

---

## 1. Positioning

CDISC's [`cdisc-org/analysis-concepts`](https://github.com/cdisc-org/analysis-concepts) repository implements the AC/DC framework: a concept model, a method library, a transformation library, an implementation catalog, an eSAP model, and a working browser-based eSAP builder with in-browser R execution. MIT / CC-BY-4.0.

**Nothing here reimplements that.** Two pieces of work sit on top of it:

**Part A — the flow snapshot.** Take real endpoints of graded complexity through the full chain, and record what the process actually costs: what is automated, what is authored, where it strains. Not a proof of concept in the sense of showing the idea can work — the framework already demonstrates that — but a record of how it would be applied to a real study, with the effort visible.

**Part B — the governance overlay.** Scope, ownership, versioning and divergence detection across catalogues, plus bidirectional lineage. The layer a sponsor deployment needs and a reference implementation reasonably lacks.

Part A comes first, and it is what motivates Part B. The strongest argument for catalogue governance is a measurement of what authoring costs without it.

---

# PART A — FLOW SNAPSHOT

## 2. Objective

Produce an artefact that answers: *if we adopted this, what would actually happen, and what would it cost?*

Three graded endpoints taken end to end, each showing:

- What the protocol and SAP specify
- What is automated, and what a human authors
- The derivation chain and analysis binding produced
- How the result compares against the ADaM that was actually built
- Where the flow strains, and why

### 2.1 Why comparison against built ADaM matters

Without ground truth the snapshot only shows the flow is internally coherent. With it, the snapshot shows whether the concept model reproduces what a statistician specified and a programmer built — and every divergence is informative. Either the model cannot express something real, or it exposes an ambiguity the SAP was carrying silently. Both are worth knowing and neither is available from a reference example.

## 3. Source study

**TORIVA-LUNG 301** — a simulated Phase 3 NSCLC trial (fictional sponsor), public at `OpenTrialReporting/torivumab-nsclc-301`. Chosen over the CDISC Pilot and over real sponsor protocols because it is the only source where protocol, SAP, programming specs and built ADaM all exist, are internally consistent, and carry no confidentiality constraint.

Available:

| Artefact | Notes |
|---|---|
| Protocol synopsis | 959 lines |
| SAP | 626 lines, nine estimands with an explicit ICH E9(R1) table |
| Programming specs | ADSL, ADAE, ADLB, ADRS, ADTR, ADTTE and others, variable-level |
| Built ADaM | Parquet datasets, 450 subjects |
| TFL shells | Cross-referenced from the specs |

The nine estimands (E1, E1a, E1b, E2, E2a, E3, E3a, E4, E5) each carry population, endpoint, intercurrent-event strategy, summary measure and statistical method. USDM has `Estimand` as a first-class class and the eSAP binds to it, so the protocol end of the chain connects through real metadata rather than assertion.

**Real sponsor protocols play a narrower role**: read their endpoint text against the three shapes below and confirm nothing important is unrepresented. No ADaM access needed for that, which suits what is available.

**The CDISC Pilot ADAS-Cog stays as a control.** Scenario 2 is already worked upstream, so when something fails it is possible to tell whether the flow broke or the endpoint did.

## 4. The endpoint ladder

### 4.1 Simple — ADLB, laboratory change from baseline

Chain: BC → `T.BaselineSelection` → `T.ChangeFromBaseline` → descriptive or ANCOVA.

Both transformations exist upstream. Expected to work with no new authoring. Its value is precisely that it is shallow: it shows the flow does not impose machinery where none is needed, which is the first objection the framework will attract.

Exercises `ParameterDimension` across many lab parameters, which a single-measure endpoint does not.

### 4.2 Moderate — ORR (estimand E3)

Chain: BC → confirmed best overall response derivation → `T.Responder_ChiSq` / `M.Proportion` / `M.CMH`.

`T.Responder_ChiSq`, `M.Proportion`, `M.CMH` and `M.FisherExactTest` all exist. The work is deriving confirmed BOR: `M.RecordSelection`, `M.Categorization` and `M.ThresholdCompare` are the primitives.

Also exercises a **composite intercurrent-event strategy** — non-responders by composite under E3 — and the E3 / E3a pair differ only in denominator population, which is a clean demonstration of one derivation serving two estimands.

### 4.3 Complex — PFS (estimand E2)

Chain: BC → PD date selection → censoring hierarchy → `M.DateDifference` → `M.KaplanMeier` / `M.CoxPH` / `M.LogRankTest`.

This is the tier that finds the limit. See §5.

### 4.4 Deliberately out of scope

**Adverse events.** A different *shape* rather than a deeper one — event observations rather than findings, counts rather than measures, OCCDS rather than BDS. Worth naming as an untested limitation; not worth the authoring cost in a snapshot.

**The other five ADTTE parameters.** ADTTE carries OS, OSWOT, PFS, PFSINV, DOR and TTR. PFS alone is the tier. OSWOT is worth a passing mention because its own spec already records a data limitation — no subsequent anti-cancer therapy captured in CM, so the SAP §13.4 censoring rule collapses to `TRTEDT + 30 days`. That is specification meeting data reality, and a flow snapshot should show it rather than hide it.

## 5. Where the flow is expected to strain

Established by inspection of the upstream libraries, not assumed.

### 5.1 No time-to-event derivation transformations exist

The transformation library contains baseline selection, change from baseline, LOCF, peak concentration, unit conversion, analysis-visit derivation and the ADAS family. **Nothing produces `AVAL` and `CNSR`.** `T.OS_LogRank` consumes time and event as though already derived.

The *methods* are present — `M.DateDifference`, `M.RecordSelection`, `M.ConditionalValue`, `M.ThresholdCompare`, `M.Aggregation`, `M.WindowLookup`. So the gap is at the transformation layer, not the method or schema layer, and closing it means authoring three or four new `T.` entries rather than extending the framework.

### 5.2 The `censoring` statistical role is declared and unused

`statisticalRole` includes `censoring`. No method uses it. `M.KaplanMeier`, `M.CoxPH` and `M.LogRankTest` each declare `time` and `event` as two separate `response` roles, with the formula carrying the meaning: `Surv(<time>, <event>) ~ <fixed_effect>`.

Functionally this works. But the metadata cannot distinguish which response is the time and which is the indicator, so any signature computed over input roles treats them as interchangeable. Worth raising upstream (§12).

### 5.3 Censoring rules are where SAP ambiguity concentrates

The ADTTE spec implements an FDA 2018 hierarchy: confirmed PD on or before data cut-off; else death without confirmed PD; else censor at last adequate assessment, with branches for new anti-cancer therapy and for two or more consecutive missed visits.

Expressible in principle as nested `M.ConditionalValue` over `M.RecordSelection`, at roughly the depth of the ADAS-Cog chain. Whether it composes cleanly is the open empirical question, and answering it is the point of this tier.

### 5.4 The BC joint is annotated, not resolved

In the upstream worked scenario, `linkedBCIds` is empty and the connection to Biomedical Concepts exists only as prose in `note` fields. Everything above that joint is machine-traceable; the last hop is not.

**Leave it visible and labelled** rather than closing it silently. It is exactly the sort of handoff a governance layer exists to police, and an honest snapshot is more useful than a complete-looking one.

### 5.5 Chain position carries meaning that individual entries do not

`T.ADAS_SumAvailableScores` and `T.ADAS_MissingScaleCapacity` are structurally identical — same method, same roles, same bindings, same configuration. What separates them is what feeds them: raw item scores in one case, the output of `T.ADAS_MissingContribution` in the other.

**Consequence for Part B:** a signature computed over a transformation in isolation cannot distinguish them. Divergence detection needs chain context. This corrects §9.3 as originally specified.

### 5.6 No study-level view exists in either source

Established by inspection of both repositories.

`ac-dc-app` is a linear wizard — fourteen views walking one endpoint at a time (study select, study config, endpoint what/how/spec/summary, transformation config, derivation pipeline, smartphrase builder, execute analysis, eSAP builder), plus the SoA matrix, which is scoped to activities and encounters rather than to analysis.

TORIVA is a pipeline producing static artefacts: `TFL-OUTPUTS.html` and `.docx`, individual tables as docx/html/rtf, figures as PNG, P21 reports, QC trackers as spreadsheets. No Shiny application, no interactive layer.

**Neither shows a study.** Nothing answers: how many endpoints are specified and how many are not, which derivations are shared between them, which estimands are covered, where a chain is complete versus annotated-only. The wizard knows the endpoint in front of you; the pipeline knows finished outputs. The middle is absent.

## 6. Method

1. Map each endpoint's chain **on paper first**, against the SAP text, before touching the wizard. If PFS does not compose on paper, that is the finding.
2. Author each tier in the eSAP builder, recording elapsed time and every point where a decision was needed.
3. Compare output against the built ADaM. Record divergences and classify each as model limitation, spec ambiguity, or authoring error.
4. Write up as a stage-by-stage flow: what the study contains, who acts, what is automated, what changes at study scale.

### 6.1 The number that matters

One endpoint, and for ADAS-Cog nine nested derivation steps, manually assembled. A real study has somewhere between ten and fifty analysis-relevant endpoints.

If each needs that treatment, the flow does not scale without a reusable chain library — which is Part B, arriving not as a nice-to-have but as a precondition. **Part A's most valuable output is the authoring cost per tier.**

### 6.2 Form of the artefact — decided

The snapshot takes the shape of the study-level view that §5.6 shows is missing: endpoints listed with coverage status, shared derivations made visible, chain completeness marked, authoring cost recorded per tier.

**Static rendering first, not an application.** A generated HTML page from the authored chains. The moment it becomes interactive, Part B has started before Part A has produced its measurement, and the measurement is the point.

**Gaps shown as prominently as completions.** Unresolved `linkedBCIds`, the absent time-to-event transformations, any endpoint that failed to compose. An artefact that only shows what worked is a sales document, not a record, and will not survive its first informed reader.

This view is also the natural first Part B screen — coverage and reuse across endpoints is precisely what catalogue governance is about — so the static version is a design probe for it, not throwaway work.

---

# PART B — GOVERNANCE OVERLAY

Deferred until Part A is complete. Retained here because Part A is designed to test its premise.

## 7. The gap

| Need | In AC/DC today |
|---|---|
| Scope a catalogue to a therapeutic area, then promote organisation-wide | Absent |
| Ownership and approval status of a method or transformation | Absent |
| Versioning with a defined breaking-change rule | Absent |
| Detecting near-duplicate methods across catalogues | Absent |
| Where-used: which transformations and studies depend on a method | Absent |
| Bidirectional lineage from protocol statement to analysis result | Absent |

Verified by inspection: no occurrences of therapeutic area, scope level, governance, approval status, owner, lineage or where-used across `model/` and `lib/`.

## 8. Overlay, not fork

**Scope, status, owner and version live in a sidecar registry keyed by AC/DC `oid`, never as added fields inside the framework's own JSON.** Forking their schemas strands the project on a divergent copy within two upstream releases.

```
upstream (read-only, git submodule at a pinned commit)
        │ keyed by oid
        ▼
overlay registry (ours, writable)
  registry_entry(oid, scope_level, scope_ref, status, owner,
                 version_major, version_minor, signature_hash)
  edge(from, to, edge_type, study_id)
```

## 9. Signature and divergence detection

### 9.1 Method signature

```
sha1(type,
     sorted(input_roles → name, statisticalRole, dataType, cardinality, required),
     sorted(configurations → name),
     sorted(output_specification.output_classes → class, sorted(statistics)),
     sorted(codings → code))
```

### 9.2 Why outputs and codings are in the key

**Empirically validated; the naive version fails.** Keying on input roles and configurations alone clusters 18 methods as identical — Mean, Median, Variance, Minimum, Maximum, Skewness, Kurtosis, Mode, Sum, Count and the rest of the univariate statistics all take a single response input with no configurations.

Adding output statistics and codings reduces this to **two clusters across 60 methods** (`M.ImputedValue_Mean`/`_Median`, `M.CumulativeFrequency`/`_Count`), both genuine consolidation candidates.

**29 of 60 methods carry no STATO coding**, so codings are a tiebreaker, never a required component.

### 9.3 Transformation signature — requires chain context

Originally specified as `usesMethod` + bindings + configurations. **This is insufficient** (§5.5): structurally identical transformations are distinguished only by their inputs' provenance. The signature must incorporate the derivation chain position, or divergence detection produces false positives on exactly the cases that matter.

Design deferred until Part A produces real chains to test against.

### 9.4 Tooling

`acdc_divergence.py` implements §9.1 and §9.2 against a repository checkout. Read-only, standard library only, with `--compare-naive` to reproduce the false-positive cluster and `--overlay` to flag cross-scope clusters.

## 10. Scope and versioning

**Three levels resolved nearest-first: study → TA → organisation.** All three exist from the first commit; organisation starts populated by the upstream library itself, which gives the model a real top tier on day one.

**Promotion changes `scope_level` on a stable `oid`; it never mints a new identity.**

Versioning ties breaks to the signature:

| Change | Effect |
|---|---|
| `input_roles` added, removed, or role attributes changed | Breaking. New major |
| `output_specification` classes or statistics changed | Breaking. Consumers map output slots |
| `configurations` added with a default | Minor |
| Descriptions, notes, assumptions | Minor |
| `formula.generic_expression` changed without role change | Minor, flagged for review |

Upstream carries no version field, so the overlay assigns `1.0` on first ingest and tracks divergence from the pinned commit thereafter.

**Governance is modelled, not built**: `status` and `owner` with recorded transitions. No workflow engine, no e-signature.

## 11. Lineage

Edges materialised on ingest:

| From | To | Edge type | Source |
|---|---|---|---|
| `Objective` | `Endpoint` | `has_endpoint` | USDM |
| `Endpoint` | `BiomedicalConcept` | `measured_by` | USDM / eSAP |
| `Activity` | `BiomedicalConcept` | `collects` | USDM `biomedicalConceptIds` |
| `BiomedicalConcept` | OC facet | `classified_as` | `bc_to_oc_instance_mapping.json` |
| `BiomedicalConcept` | SDTM Dataset Specialization | `tabulated_as` | `sdtmDatasetSpecialization` extension |
| OC | DC | `input_to` | Transformation bindings |
| Transformation | Method | `uses_method` | `usesMethod` |
| Transformation | DC / AC | `instance_of` | `instanceOf` / `acCategory` |
| Method output slot | AC | `produces` | `methodOutputSlotMapping` |
| `Estimand` | `StudyAnalysis` | `analysed_by` | eSAP |
| Concept | ADaM variable | `realised_as` | `concept-variable-mappings.json` |

Recursive CTEs over an edge table. No graph database until path queries routinely exceed four hops.

## 12. Upstream contribution

Two findings from Part A are worth raising as issues on `cdisc-org/analysis-concepts` regardless of whether Part B proceeds:

1. **The unused `censoring` statistical role** (§5.2)
2. **No time-to-event derivation transformations** (§5.1) — with the PFS chain from Part A as a concrete proposal if it composes

Arriving with findings about their library is a better opening than arriving with a proposal, and it establishes the work is real.

**Design for contribution regardless of whether it happens**: overlay UI in vanilla JS matching upstream module conventions; no organisation-specific content in the registry schema; local specifics confined to one configuration file. Near-zero cost, and skipping it means a permanent fork.

---

## 13. Non-goals

- **Do not reimplement the concept, method or transformation models.** Consume upstream.
- **Do not fork upstream schemas to add fields.** Overlay only.
- **No SoA views.** Protocol and Detailed SoA exist upstream.
- **AC/DC JSON metadata is the system of record.** DSL alternatives — notably `metadatadriven/acdc-wip` (Thunderstruck) — are out of scope. Two representations would leave any registry governing half the assets. That repository's README also states MIT while its `LICENSE` file is AGPL-3.0; the network clause is a material obstacle for an internally hosted service and the discrepancy is unresolved.
- **Do not redistribute CDISC Library content.** The cache is gitignored upstream by design; each developer regenerates it with their own key.
- **No ARS implementation.** ARS v2 is expected. The eSAP `ARSAnalysisRef` hook exists and is left alone.
- **No protocol authoring or digitisation.** USDM fragments are hand-authored for the endpoints in scope; full protocol digitisation is a separate project and a separate argument.
- **No GxP validation posture.** No workflow engine, e-signature or validation package.
- **No interactive dashboard during Part A.** The snapshot is a static rendering (§6.2). Building an application is Part B work and would consume the measurement Part A exists to produce.

## 14. Architecture (Part B)

Upstream is a vanilla-JS SPA with no backend, executing R in-browser via WebR. Consequently: **no R sidecar is needed**, and a backend is required only for the registry's persistence and cross-study queries.

| Layer | Choice |
|---|---|
| Upstream | pinned git submodule, read-only |
| Registry service | Python 3.12 + FastAPI |
| Store | SQLite; `registry_entry` and `edge` tables |
| USDM handling | `cdisc-org/usdm`; CORE rules for conformance |
| UI | Extend `ac-dc-app` in vanilla JS |
| Graph view | Cytoscape.js |
| Execution | WebR, upstream, untouched |

`make upstream-bump` retargets the submodule, re-runs ingest and emits a signature diff — the version-review queue, making upstream bumps a reviewable event rather than a merge conflict.

## 15. Next actions

1. **Map the PFS censoring hierarchy on paper** against SAP §13.5 and §4.1–4.4, as nested `M.ConditionalValue` over `M.RecordSelection`. If it composes, the complex tier is viable. If not, that is the finding.
2. **Stand up `ac-dc-app` locally** — `python3 ac-dc-app/serve.py`, and point `studies.json` at `CDISC_Pilot_Study_soa_enriched.json` or the SoA views will look broken.
3. **Hand-author USDM fragments** for the three TORIVA endpoints — objective, endpoint, estimand, BCs. Not a full study definition.
4. **Author the simple tier first**, to calibrate the effort measurement before attempting the complex one.
5. **Check real sponsor protocols' endpoint text** against the three shapes, for breadth.

## 16. Open questions

1. **How many endpoints would realistically go through this on a typical study?** Ten and fifty give different conclusions about whether Part B is optional.
2. **Which internal TA list is authoritative**, and does it map to USDM `businessTherapeuticAreas`? Blocks Part B only.
3. **CDISC Library API keys** — available? Not needed for Part A.
4. **Audience for the snapshot** — a standards group will respond to divergence findings; a delivery organisation will want lineage first. Different emphasis, same artefact.
5. **Host for the study-level view.** ADSL Explorer is in flight and may already have a study-overview shell. If far enough along, extending it is cheaper than starting fresh, and it would place the concept-model view alongside the data view — arguably where it belongs. Affects §6.2 only in delivery, not in content.

---

## 17. Revision history

**v0.3** — Added Part A, the flow snapshot, as the near-term work; deferred Part B. Selected TORIVA-LUNG 301 over the CDISC Pilot for ground-truth comparison. Added the endpoint ladder and the expected-strain findings (§5). Corrected transformation signature design: chain position carries meaning that individual entries do not (§5.5, §9.3). Recorded that neither source repository has a study-level view (§5.6), and fixed the artefact's form as a static study-level rendering rather than an application (§6.2).

**v0.2** — Repositioned from a standalone build to an overlay on `cdisc-org/analysis-concepts`. Corrections from the earlier draft:

| v0.1 | Correction |
|---|---|
| DC ambiguous between Derivation and Data Collection Concept | DC is **Derivation Concepts**. `DataCollectionConcept` removed |
| AC = "what question is being answered" | AC is an aggregated, non-subject-level **result** hierarchy. The object described was a **Transformation** |
| Own `AnalysisMethod` with invented role vocabulary | Upstream `Method` with closed `statisticalRole` enum; dimensional role belongs on the binding as `dataStructureRole` |
| Declarative-vs-template as an open fork | Resolved upstream: declarative formula on the method, call templates in the implementation catalog |
| No Observation Concept | OC is the atomic unit; BC→OC mapping exists |
| Signature = input roles + parameters | Insufficient. Clusters 18 distinct statistics |
| R sidecar via plumber | Unnecessary; WebR executes client-side |
| Python + React, new build | Extend the existing vanilla-JS app |
| Build an SoA screen | Protocol and Detailed SoA already exist upstream |
| Construct BC → SDTM mapping | Carried by the `sdtmDatasetSpecialization` USDM extension |
| Bundle cached CDISC Library fixtures | Would redistribute Library content |
