# Human review plan

Nothing in this repository has been reviewed by a human. This plan says what to review, in what
order, what specifically to check, and what to skip.

**The backlog looks like thirteen findings. The critical path is one issue.** Only Issue 4 is
recommended for filing, so only Issue 4 and its evidence chain block anything. Everything else
can wait, and some of it should never be filed at all.

---

## 1. The situation in numbers

| | |
|---|---|
| Findings | 13, none reviewed |
| **Findings whose premise or proposed fix has been disproved** | **5** — F01, F02, F04, F07, F09 |
| Of those, drafted for public filing before being caught | 4 |
| Caught by the first verification pass | 2 (F02, F04) |
| Caught later, by unrelated work | 3 (F01, F07, F09) |
| Upstream issues drafted / filed | 5 / 0 |
| Issue candidates not drafted | 5 (F09–F13) |
| Discrepancies found in TORIVA | 13, all open |
| Tiers with all four method steps complete | 1 of 3 |

The disproof rate is the reason this plan exists. Two of five were caught by the process; three
were not, and surfaced only because unrelated work happened to touch them.

## 2. What only a human can do

Re-reading the findings for correctness is worth something, but it is not the scarce thing. Four
judgements cannot be delegated:

1. **Is this claim worth making to these maintainers?** A true finding filed in the wrong tone,
   or at the wrong scale, damages the relationship the project exists to build
   (specification §12).
2. **Is the clinical or statistical reading right?** Several findings rest on domain judgements
   an AI should not be trusted with unreviewed — see §6.
3. **Is the framing fair?** F13 in particular says a reference implementation is missing things
   it may never have intended to have.
4. **Who accepts the reputational risk** of a public issue against `cdisc-org`.

## 3. The five ways this repository has actually been wrong

Use these as a lens on any finding, rather than reading for general plausibility. Each has
produced at least one real error here.

| # | Failure mode | Instances | The check |
|---|---|---|---|
| **A** | Application behaviour inferred from library JSON | F04, F05, F09 | Has the app been *run* for this claim? If not, treat the claim as unverified |
| **B** | One level of a structure read, a conclusion drawn about another | F04 (endpoint vs terminal `linkedBCIds`), F01 (method vs transformation outputs) | Was the *whole* structure enumerated, or one instance? |
| **C** | Method surface confused with authoring surface | ORR mapping, PFS mapping | Does "composes" mean the method exists, or that a chain can be built? See F13 |
| **D** | A fix proposed that a counter-example in the same study breaks | F07 | Was the suggestion tested against a second case before being written? |
| **E** | History asserted without checking it | F02 | Was `git log -S` run, to distinguish *removed* from *never present*? |

Every finding carries a reproduce command. **Re-running them is the cheapest first pass** and
catches nothing of class A or D, which is precisely why the classes matter.

---

## 4. Tier 1 — the critical path (blocks filing Issue 4)

Target: about two hours. Everything here must pass before anything is filed publicly.

- [ ] **`docs/findings/upstream-issues.md` — Issue 4 text.** Read as a maintainer would.
      Specifically: is the tone that of a collaborator reporting a gap, or an auditor reporting
      a defect?
- [ ] **Restructure Issue 4 to lead with the requirement, not the suggestion.** Issue #9 on the
      upstream tracker records the maintainer rejecting an issue that *"specified solution
      choices before the requirements were stated"*. Every draft here leads with a
      **Suggestion**. This is the single highest-value edit in the plan.
- [ ] **`F08` — the upstream half.** Re-run the search: no difference-of-proportions statistic
      in `statistics_vocabulary.json`, `M.CMH` yields an odds ratio. Mechanical, ten minutes.
- [ ] **`F08` — the ICH E9(R1) reading.** *Needs a statistician.* The claim is that substituting
      an odds ratio for a risk difference answers a different question because the
      population-level summary is an estimand attribute. Is that right, and is it right in a way
      a CDISC maintainer would accept without argument?
- [ ] **The TORIVA premise.** SAP §5.3 and §13.6 both specify a stratified MH risk difference —
      verified verbatim on 2026-09-16. Confirm the quotes are not being read out of context.
- [ ] **D13.** SAP §13.6 names `stats::mantelhaen.test()` as the estimator, which returns an
      odds ratio, not a risk difference. Confirm — and decide whether to mention it in the
      issue. It strengthens the argument and it also advertises an error in our own source
      study.
- [ ] **STATO_0000424.** Confirm it is the right term and that offering it is helpful rather
      than presumptuous.
- [ ] **Decide: file one, or none yet.** The standing recommendation is Issue 4 alone, then
      wait. Four issues in the upstream tracker's lifetime, one active maintainer.

**Exit condition:** Issue 4 restructured, its two factual halves confirmed, and a named person
willing to post it.

---

## 5. Tier 2 — before any further filing

Only needed if Tier 1 goes well and more issues are wanted. Roughly half a day.

- [ ] **F02** — the surviving claim is the `time`/`event` role collision. Check the consequence
      is stated as *our* tooling need, not as a defect in theirs (Issue 1's weakness).
- [ ] **F06** — the largest and most robust finding. Check the three quoted method fragments,
      and check nothing on the `estimands_01` branch supersedes it.
- [ ] **F01 as corrected** — the output-cardinality argument was false and is now rewritten
      around `T.UnitConversion`'s facet pattern. **Failure mode B.** Confirm the facet reading is
      right before Issue 3 asks maintainers about it.
- [ ] **F07 as amended** — *needs a clinician or oncology statistician.* Is `LOW = HIGH >
      NORMAL` genuinely analysis-specific rather than a property of `NRIND`? The amendment, and
      Issue 5's fix, both turn on this.
- [ ] **Issues 1, 2, 3, 5** — same restructure as Issue 4: requirement first.
- [ ] **Check `estimands_01` again at filing time.** It was moving fast; `main` has not moved
      since 2026-06-17.

## 6. Tier 3 — internal correctness, nothing public at stake

A day, and it can be sampled rather than done exhaustively.

| Item | What to check | Failure mode |
|---|---|---|
| F09 | Corrected **twice** in one day. The surviving claim is `time_order` single-cardinality with no tie-break. Everything else has been withdrawn once already | A |
| F12, F13 | Both rest on running the app. Re-run the four clicks; they are recorded in the logs | A, C |
| F10, F11 | Never independently checked by anyone, including by later work | B |
| F03, F05 | Confirmed early and untouched since | — |
| `endpoints/*/mapping.md` | Do they now say **on which surface** a step composes? Two needed correcting | C |
| `endpoints/01-simple-lab-cfb/comparison.md` | The 71% / 96.8% / 21.3% figures. Re-run `tools/check_baseline_ambiguity.py` | — |
| `chain.json` ×2 | Both were reassembled from browser output and verified byte-exact. Spot-check one against a fresh authoring run | — |

## 7. Tier 4 — record hygiene

Lowest stakes, but PROVENANCE governs whether anything gets filed, so it should not stay
unread indefinitely.

- [ ] `PROVENANCE.md` §5 (inference vs measurement) and §7 (limitations) — the two sections that
      constrain everything else.
- [ ] `docs/method.md` — particularly *Two libraries, two questions*, added after the surface
      confusion was found.
- [ ] `README.md` findings summaries against the finding files.
- [ ] `docs/specification.md` §5 and §17 — already marked superseded; confirm the disposition
      table still matches.

## 8. Which claims need which expertise

| Needs | Claims |
|---|---|
| **Statistician** | F08's ICH E9(R1) reading; F07's ordering question; whether the chi-squared substitution in ORR's `chain.json` is as wrong as the log says |
| **Oncology / RECIST** | F07's `CR ≺ PR ≺ SD ≺ PD ≺ NE`; the shift table's `LOW = HIGH` collapse |
| **Someone who has used `ac-dc-app`** | F05, F09, F12, F13 — everything of failure mode A |
| **Careful reader, no domain needed** | F01, F02, F03, F06, F10, F11; all counts and reproduce blocks |
| **You, as the author of TORIVA's specs** | D1–D13. You wrote the programming specs, which `study/README.md` flags as a bias risk |

## 9. What not to review

Saying this explicitly so effort does not go to the wrong places.

- **F04.** Retired, not filed, superseded by F03. Read the disposition, not the finding.
- **The four unfiled issue candidates** (F09–F13 in `upstream-issues.md`). They are recorded as
  candidates precisely so they need no decision yet.
- **`tools/check_consistency.py` output.** The pre-commit hook runs it; it is green.
- **PFS `comparison.md` / `log.md`.** They do not exist, correctly — there is nothing to author.
- **F13 as an issue.** Recorded as probably not filable as written. Review the *finding* if you
  want the numbers; do not spend time drafting it.

## 10. Sign-off

Nothing here is reviewed until a line is filled in.

| Item | Reviewer | Date | Outcome |
|---|---|---|---|
| Tier 1 — Issue 4 | | | |
| F08, statistical reading | | | |
| F07, ordering question | | | |
| Tier 2 — Issues 1, 2, 3, 5 | | | |
| Tier 3 — findings sample | | | |
| Tier 4 — PROVENANCE §5, §7 | | | |

When Tier 1 is signed off, update `PROVENANCE.md` §7.1, which currently says nothing has been
human-reviewed, and the review-status row in §2.
