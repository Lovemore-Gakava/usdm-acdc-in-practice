# Findings

Each finding was re-verified against the pinned upstream commit before being written up.
Verification commands and their output are recorded in each file so any claim can be re-run.

| ID | Claim | Status at `739344c` |
|---|---|---|
| [F01](F01-no-tte-derivation-transformations.md) | No time-to-event derivation transformations exist | **Confirmed in part** — the library gap holds; its output-cardinality argument was false and is corrected |
| [F02](F02-time-event-role-collision.md) | The `censoring` statistical role is declared and unused | **Corrected** — never declared; the consequence holds, the premise does not |
| [F03](F03-chain-position-carries-meaning.md) | Chain position carries meaning individual entries do not | **Confirmed, strengthened** |
| [F04](F04-bc-joint.md) | The BC joint is annotated, not resolved | **Retired** — it is resolved |
| [F05](F05-no-analysis-coverage-view.md) | No study-level view exists | **Restated** — one exists; it carries no analysis state |
| [F06](F06-no-general-predicate.md) | No general predicate exists over multiple variables | **New** — blocks the PFS tier, and ORR's confirmation rule |
| [F07](F07-ordering-is-unstated.md) | `best`/`worst` presuppose an ordering the metadata does not carry | **New, amended** — the lab tier contradicts its own proposed fix |
| [F08](F08-no-risk-difference.md) | No difference-of-proportions statistic exists | **New** — blocks estimand E3's summary measure |
| [F09](F09-record-selection-has-no-tiebreak.md) | Record selection carries no tie-break, and no transformation binds its ordering | **New** — found mapping the lab tier |
| [F10](F10-visit-windows-are-enumerated-not-generated.md) | Visit windows must be enumerated, and nothing may escape windowing | **New** — found mapping the lab tier |
| [F11](F11-analysis-record-flag-has-no-transformation.md) | The model names `ANL01FL` and nothing produces it | **New** — found mapping the lab tier |

Two of the five original findings did not survive verification, and one was retired outright.
F02 and F04 were both slated for upstream issues; filing them as originally written would
have been wrong. This is the reason the verification step exists.

F06 through F11 came out of mapping endpoints on paper rather than from inspecting the
libraries — which is the case for step 1 of the method. F06 in particular was found on PFS and
then confirmed independently on ORR and on the lab tier, so the predicate gap is a general
derivation problem rather than a time-to-event one.

**The lab tier corrected two findings as well as adding three.** F01's output-cardinality
argument was false — two derivation methods declare multiple coordinated output classes, and
one of them belongs to a transformation F01 itself cites. F07's proposed fix was contradicted
by a table in the same study. Both had been drafted as upstream issues; both issue texts were
rewritten. That is now three wrong premises caught before filing (F02, F04, F01) and two
proposed fixes withdrawn (F04, F07).

Pinned commits: upstream `739344ca31203bb502efeee2b855286e17977be6` (2026-06-17),
TORIVA-LUNG 301 `8534339d95d6e1709f5def1e715a9b0c8cc06fe8` (2026-07-29).
