# F02 — Time and event are indistinguishable in method metadata

**Status: corrected.** The consequence holds. The premise does not.

## What was originally claimed

> `statisticalRole` includes `censoring`. No method uses it.

## What is actually true

There is no `censoring` value in the enum. `StatisticalRole` in
`model/method/acdc_methods.schema.json` (schema v0.8.0) is:

```json
{
  "title": "StatisticalRole",
  "description": "The statistical role of an input variable",
  "type": "string",
  "enum": ["response", "covariate", "fixed_effect",
           "repeated_factor", "repeated_subject", "strata", "offset"]
}
```

It has never contained `censoring`:

```
$ git log --all -S'censoring' -- model/method/acdc_methods.schema.json
(no commits)
```

The string `censoring` appears upstream only on the unmerged `estimands_01` branch
(Stuart Malcolm, 2026-08-14), where it is an **intercurrent-event implementation anchor**
on an ICH E9(R1) strategy smartphrase, not a statistical role:

```js
oid: "SP_ICE_WHILE_ON_TREATMENT",
anchors: { icheStrategy: "WhileOnTreatment", implementation: "censoring" }
```

Elsewhere `censor` appears only as the output statistic `n_censored`, and in prose
(`"Non-informative censoring"` as a `M.KaplanMeier` assumption; `"Event indicator
(1=event, 0=censored)"` as a role description).

## The consequence is unchanged, and is the part that matters

All three survival methods declare `time` and `event` as two separate `response` roles:

| Method | `input_roles` (name, statisticalRole) | Formula |
|---|---|---|
| `M.KaplanMeier` | time→`response`, event→`response`, fixed_effect→`fixed_effect` | `Surv(<time>, <event>) ~ <fixed_effect>?` |
| `M.CoxPH` | time→`response`, event→`response`, covariate→`covariate`, fixed_effect→`fixed_effect`, strata→`strata` | `Surv(<time>, <event>) ~ <covariate>* + <fixed_effect>+ + …` |
| `M.LogRankTest` | time→`response`, event→`response`, fixed_effect→`fixed_effect`, strata→`strata` | `Surv(<time>, <event>) ~ <fixed_effect>+ + <strata>*` |

Meaning is carried entirely by position in the formula string. Functionally this works —
the formula is unambiguous to a reader and to the execution layer. But any signature computed
over input roles sees two identical `response` entries and cannot tell which is the time and
which is the indicator. Swapping them produces an identical signature and a nonsense analysis.

## Incidental: `offset` is the role that is declared and unused

Frequency of `statisticalRole` across all 60 methods:

| Role | Count |
|---|---|
| *(absent)* | 38 |
| `response` | 42 |
| `fixed_effect` | 37 |
| `covariate` | 4 |
| `strata` | 3 |
| `repeated_subject` | 3 |
| `repeated_factor` | 2 |
| **`offset`** | **0** |

`offset` is declared in the enum and used by no method. That is the finding F02 was
reaching for, attached to the wrong role — and it is a much smaller one, since an
unused enum value with no consumer is unremarkable.

## Effect on the upstream issue

The issue as originally drafted asserted a declared-but-unused `censoring` role. Filing it
would have been incorrect. The issue worth filing is the role collision between `time` and
`event`. See [upstream-issues.md](upstream-issues.md).
