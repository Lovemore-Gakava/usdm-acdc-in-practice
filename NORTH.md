# NORTH — what this project is for

Read this before starting any piece of work. It is the only document that says what "done"
means; everything else describes how.

**How it got here** — every dated decision, in order — is [`docs/decisions.md`](docs/decisions.md).
This file is the destination and the scoreboards, and is kept short on purpose.

---

## Destination

> **Understand USDM and ICH M11, and the AC/DC/BC framework, well enough to explain and
> demonstrate them — by structuring one protocol and taking one endpoint the whole way
> through.**

## Finish line

Done means all nine green, on at least one endpoint. Nothing else counts as finishing.

Every table below is **computed from the filesystem** by `tools/check_consistency.py`, which
the pre-commit hook runs. It cannot quietly say ✓ for something that has not happened, and the
scoreboard prints on every commit.

### Endpoint 1 — laboratory change from baseline

<!-- north:status -->

| # | Stage | Status |
|---|---|---|
| 0 | Protocol mapped to ICH M11 elements | ✓ |
| 0b | Protocol restructured to M11, USDM regenerated from it | ✓ |
| 1 | USDM fragments hand-authored | ✓ |
| 2 | BC linked on the chain's terminals | ✓ |
| 3 | DC — derivation authored | ✓ |
| 4 | AC — analysis bound | ✓ |
| 5 | eSAP generated | ✓ |
| 6 | Executed, a real result produced | ✓ |
| 7 | Compared against built ADaM | ✓ |

<!-- /north:status -->

### Endpoint 2 — systolic blood pressure, change from baseline, MMRM

<!-- north:status:vitals -->

| # | Stage | Status |
|---|---|---|
| 0 | Protocol mapped to ICH M11 elements | ✓ |
| 0b | Protocol restructured to M11, USDM regenerated from it | ✓ |
| 1 | USDM fragments hand-authored | ✓ |
| 2 | BC linked on the chain's terminals | ✓ |
| 3 | DC — derivation authored | ✓ |
| 4 | AC — analysis bound | ✓ |
| 5 | eSAP generated | ✓ |
| 6 | Executed, a real result produced | ✓ |
| 7 | Compared against built ADaM | ✓ |

<!-- /north:status:vitals -->

### Phase 2 — fix the study, digitise the protocol, verify alignment

> **Make TORIVA's study documents right and digital, and show that they agree.**

<!-- north:status:phase2 -->

| # | Stage | Status |
|---|---|---|
| P0 | Gap register — every discrepancy with a disposition | ✓ |
| P1 | Protocol fully M11 — all 14 sections covered | ✓ |
| P2 | USDM generated from it, with the schedule of activities | ✓ |
| P3 | Alignment verified by a tool | ✓ |
| P4 | Hands-on walkthrough written | ✓ |
| P5 | Both endpoints re-run on the aligned study | ✓ |
| P6 | The documents made correct — six decisions applied, sources marked | ✓ |
| P7 | Re-pinned to the corrected source after #27 — 0 warn, runs stamped with the pin | ✓ |

<!-- /north:status:phase2 -->

### Phase 3 — the guide

**Decided 2026-09-26 by LG.** A different destination again, so it gets its own finish line:

> **Teach the traverse to someone who has never seen it** — protocol to executed result, as a
> site anyone in pharma can follow without CDISC background, generated from the factory so it
> cannot drift from what the repository actually does.

One repository: the showroom out front, the factory behind it, so a reader who wants to see how
the material was produced can step through. Scoring is `phase3_stages` in
`tools/check_consistency.py`; the reasoning is in [`docs/decisions.md`](docs/decisions.md).

<!-- north:status:phase3 -->

| # | Stage | Status |
|---|---|---|
| G0 | Anti-drift checker exists — every figure traced to a results file | ✓ |
| G1 | A chapter per stage, each with its four sections filled | ✓ |
| G2 | Setup chapter names entry points that exist | ✓ |
| G3 | Terms glossed or linked, never assumed | ✓ |
| G4 | Every endpoint with a result has a chapter | ✓ |
| G5 | check_guide.py at 0 fail — no figure typed by hand | ✓ |
| G6 | The feedback-loop chapter — structuring a protocol is itself a quality process | ✓ |
| G7 | Published as a site, linked from the README | ✓ |

<!-- /north:status:phase3 -->

## The test

Applied to any proposed piece of work, **before starting it**:

> ### Which numbered stage does this advance?

**No number → it does not get done.** It goes in an appendix, or nowhere.

The test is deliberately harder to satisfy than "is this useful?" — nearly anything can be
argued useful. A stage number is a fact.

## This project is not

Naming these because the project drifted into all three once, and the drift was invisible while
it happened.

- **An audit of `cdisc-org/analysis-concepts`.** Their repository is the thing being learned,
  not the thing being assessed.
- **A governance or tooling product.** Part B of the specification is deferred and stays
  deferred until the finish line is green.
- **A critique.** Findings are a **by-product**: recorded when they block a stage, never
  pursued for their own sake, never the measure of progress.

## Standing questions

Asked at the start of a session, and before any new artefact:

1. Which stage does this advance?
2. What did I learn about **the framework** — not about its gaps — from the last piece of work?
3. Is the findings count growing faster than the stage count?

If (2) is answered three times running with "that it cannot do X", the project has drifted
again.
