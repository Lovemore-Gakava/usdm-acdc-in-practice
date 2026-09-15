# F05 — No analysis-coverage view exists

**Status: restated.** A study-level view exists. It carries no analysis state.

## What was originally claimed

> `ac-dc-app` is a linear wizard — fourteen views walking one endpoint at a time …
> **Neither shows a study.**

## What is actually true

There are fourteen views, and one of them is `js/views/study-overview.js` (357 lines).
It renders four tabs:

| Tab | Content |
|---|---|
| Summary | Study information, study rationale |
| Arms | Treatment arms with counts |
| Objectives | Objective → endpoint hierarchy, each endpoint with a Primary/Secondary badge and its text |
| Configuration | Concept-to-variable mappings |

So a study-level view does exist, and it does show the objective/endpoint structure.

## What it does not show, which is the part that matters

`renderObjectives()` emits, per endpoint: a checkbox, a name, a level badge, and the
endpoint text. Nothing else. The checkbox is a **selection** control — it feeds
`#btn-proceed-esap`, which carries the chosen endpoints into the eSAP builder.

It is a pre-authoring selection screen. It carries no authoring state at all:

- no indication whether an endpoint has an authored chain
- no indication whether that chain is complete or partial
- no view of which derivations are shared between endpoints
- no estimand coverage
- no authoring cost

The wizard knows the endpoint in front of you. The overview knows which endpoints exist
and lets you pick one. Neither knows what has been done across the study.

TORIVA is unchanged from the original claim: a pipeline producing static artefacts
(`TFL-OUTPUTS.html`, docx/rtf tables, PNG figures, P21 reports, QC spreadsheets).
No interactive layer.

## Consequence

The gap is narrower than stated but real, and it sharpens what `snapshot/index.html`
should be. Not "a study-level view", which exists — but a **coverage** view: endpoints
against authoring status, shared derivations made visible, chains marked complete versus
annotated-only, cost per tier recorded.

That also makes it a cleaner design probe for the first Part B screen, since coverage and
reuse across endpoints is precisely what catalogue governance is about, and it is the axis
the existing overview does not have.
