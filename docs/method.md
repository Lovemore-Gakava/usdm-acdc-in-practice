# How the findings were verified

Every finding in `docs/findings/` was re-checked against the pinned upstream commit before
being written up, rather than carried forward from the specification. Each file records the
commands and their output.

This was not a formality. Of the five findings inherited from the specification:

| | |
|---|---|
| Confirmed | F01 *(in part — see below)*, F03 |
| Premise wrong, consequence intact | F02 |
| Retired | F04 |
| Overstated, restated | F05 |
| Found during verification | F06 |

**And verification is not a one-pass step.** F01 was confirmed in that first pass and its
output-cardinality argument was still false: `M.UnitConversion` and `M.WindowedVisitAssignment`
declare two and three coordinated output classes, where F01 asserted every derivation method
declares one. It was caught only when the lab tier put `M.WindowedVisitAssignment` under the
same scrutiny for an unrelated reason — and the counter-example was a transformation F01
already cited by name. F07's proposed fix fell the same way, to a table in the study it was
drawn from.

Running total: five findings whose premise or fix did not survive — F01, F02, F04, F07, F09 —
four of them drafted as upstream issues. F09 was written and corrected the same day.

Three of the five (F04, F05, F09) failed the same way: a claim about the **application**
inferred from reading **library JSON**. That is now a named hazard. A claim about what an author
can do in the builder is not established until the builder has been run.

F09 then proved the point twice over. Its first correction was itself a source read, and when
the app was actually served on 2026-09-16 that correction was **also** wrong in two of its three
parts: the derivation pipeline does carry an add control, and `T.LOCF_Imputation` does supply an
ordering — under the role name `order`, which its method does not declare. Only the core
capability claim survived. **Two corrections, both on the day of writing, and only the run
settled it.**

The rule this yields: *serve the app before asserting anything about authoring.* It is cheap —
`python ac-dc-app/serve.py`, one endpoint, four clicks — and it has now overturned or sharpened
a claim every time it has been done.

The pass rate of confident-sounding claims in this repository is not high, and that is the
argument for the step.

F02 and F04 were both slated to be filed as issues on `cdisc-org/analysis-concepts`
(specification §12). F02 asserted a declared-but-unused `censoring` statistical role that has
never existed in the enum; F04 asserted an unresolved BC joint that is in fact resolved on
every measure terminal of the worked scenario. Filing either would have been wrong in public,
against the repository whose maintainers the project wants to work with — and specification
§12 makes the reputational stake explicit: *"arriving with findings about their library is a
better opening than arriving with a proposal."*

That is the case for the verification step, and for keeping the evidence in the files.

## What counts as evidence

- A claim about the **shape** of the model cites the schema at the pinned commit, by path
  and `$defs` name.
- A claim about **contents** cites a count or a string frequency reproducible by a command in
  the file.
- A claim about **history** uses `git log -S` over the submodule, which distinguishes
  *removed* from *never present*. F02 turned on this.
- A claim about the **application** cites file and line.

## Two libraries, two questions

Steps 1 and 2 do not read the same thing, and conflating them produced wrong conclusions on two
of three tiers.

**Step 1 reads the method library** and answers *can the model express this*.
**Step 2 reads the transformation library and the builder** and answers *can a chain be built*.

At `739344c` those differ sharply: 39 of 60 methods have no transformation, and the builder can
neither create a transformation nor reconfigure a shipped one
([F13](findings/F13-authoring-surface-is-narrower-than-the-model.md)). So a step-1 verdict of
"composes" carries no implication that anything can be authored, and both ORR's mapping and
PFS's had to be corrected on that point after the fact.

Where a mapping says a step composes, it should now say **on which surface**.

## Sequencing rule

The method's four steps are ordered, and the order is load-bearing: `mapping.md` is written
against the SAP text before the builder is opened, because doing it afterwards makes a
negative result uninterpretable.

The same rule was applied to the source study's own discrepancies. D1 and D2 (see
`study/source-refs.md`) were found while mapping PFS and deliberately **not** resolved by
looking at the built ADaM, because resolving them by inspection before authoring would
contaminate the step-3 comparison. They are recorded as open and carried forward.

## Checking the documents against the repository

The rule above applies to claims about upstream. It applies equally to the claims this
repository makes about *itself* — how many findings exist, how many issues are drafted, how
many discrepancies are recorded, how many endpoints are mapped. Every one of those is
derivable from the filesystem, so none of them is maintained by hand:

```
python tools/check_consistency.py
```

Ground truth is the filesystem; the documents are what get corrected. The checker also
verifies that every finding file appears in both findings tables, that every relative link
resolves, that every tracked file is named in `PROVENANCE.md`, and that the submodule is
checked out at the commit the documents pin.

A pre-commit hook runs it, refusing any commit that leaves the documents inconsistent.
Git does not carry hooks across a clone, so each checkout enables it once:

```
git config core.hooksPath .githooks
```

Bypass a single commit with `git commit --no-verify`. An uninitialised submodule warns rather
than fails — that is a state of your working copy, not a defect in the documents, and it should
not stop a collaborator committing a typo fix.

Lines under a *Change log* heading are exempt automatically, and any line can be exempted
with a `<!-- consistency:ignore -->` marker — a change log records what was true at each
version, so its numbers are meant to be stale.

**What it does not check is whether a claim is still true.** Nothing in it would have caught
F02's premise being wrong, or the prediction that ORR would hit F06 "less severely". Counts
are mechanical; claims need the verification pass. The checker exists so that the cheap half
never consumes attention that the expensive half needs.

## Reproducing

```
git submodule update --init
python3 tools/acdc_divergence.py --repo upstream/analysis-concepts --compare-naive
```

Expected at `739344c`: 60 methods, 25 transformations, 29/60 methods carrying no STATO
coding; 2 method clusters on the full signature, 3 on the naive signature (one of 18 entries);
1 transformation cluster, which is the F03 false positive.
