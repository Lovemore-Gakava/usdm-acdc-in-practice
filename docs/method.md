# How the findings were verified

Every finding in `docs/findings/` was re-checked against the pinned upstream commit before
being written up, rather than carried forward from the specification. Each file records the
commands and their output.

This was not a formality. Of the five findings inherited from the specification:

| | |
|---|---|
| Confirmed | F01, F03 |
| Premise wrong, consequence intact | F02 |
| Retired | F04 |
| Overstated, restated | F05 |
| Found during verification | F06 |

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

## Sequencing rule

The method's four steps are ordered, and the order is load-bearing: `mapping.md` is written
against the SAP text before the builder is opened, because doing it afterwards makes a
negative result uninterpretable.

The same rule was applied to the source study's own discrepancies. D1 and D2 (see
`study/source-refs.md`) were found while mapping PFS and deliberately **not** resolved by
looking at the built ADaM, because resolving them by inspection before authoring would
contaminate the step-3 comparison. They are recorded as open and carried forward.

## Reproducing

```
git submodule update --init
python3 tools/acdc_divergence.py --repo upstream/analysis-concepts --compare-naive
```

Expected at `739344c`: 60 methods, 25 transformations, 29/60 methods carrying no STATO
coding; 2 method clusters on the full signature, 3 on the naive signature (one of 18 entries);
1 transformation cluster, which is the F03 false positive.
