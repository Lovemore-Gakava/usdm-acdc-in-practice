# Findings

Each finding was re-verified against the pinned upstream commit before being written up.
Verification commands and their output are recorded in each file so any claim can be re-run.

| ID | Claim | Status at `739344c` |
|---|---|---|
| [F01](F01-no-tte-derivation-transformations.md) | No time-to-event derivation transformations exist | **Confirmed** |
| [F02](F02-time-event-role-collision.md) | The `censoring` statistical role is declared and unused | **Corrected** — never declared; the consequence holds, the premise does not |
| [F03](F03-chain-position-carries-meaning.md) | Chain position carries meaning individual entries do not | **Confirmed, strengthened** |
| [F04](F04-bc-joint.md) | The BC joint is annotated, not resolved | **Retired** — it is resolved |
| [F05](F05-no-analysis-coverage-view.md) | No study-level view exists | **Restated** — one exists; it carries no analysis state |
| [F06](F06-no-general-predicate.md) | No general predicate exists over multiple variables | **New** — blocks the PFS tier |

Two of the five original findings did not survive verification, and one was retired outright.
F02 and F04 were both slated for upstream issues; filing them as originally written would
have been wrong. This is the reason the verification step exists.

Pinned commits: upstream `739344ca31203bb502efeee2b855286e17977be6` (2026-06-17),
TORIVA-LUNG 301 `8534339d95d6e1709f5def1e715a9b0c8cc06fe8` (2026-07-29).
