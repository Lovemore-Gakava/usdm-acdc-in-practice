#!/usr/bin/env python3
"""
check_baseline_ambiguity.py — test F12 against built ADaM.

The AC/DC concept model reaches the baseline value of a change-from-baseline chain
only through T.ChangeFromBaseline's `parameter_baseline` slice, which constrains
`AnalysisVisit = {baseline_visit}`. ADaM, and TORIVA's SAP §12.3, define it instead
as the value of the record flagged ABLFL — the last non-missing assessment on or
before first dose, regardless of visit.

This script asks whether those two definitions pick the same record, on real data.

If `AnalysisVisit = Baseline` selects more than one record per subject × parameter,
the model's definition is under-determined and the chain is ambiguous where the SAP
is not. The script reports how often that happens, whether the candidate records
carry different values, and how large the resulting error in BASE would be.

It also reports the columns named by ADLB-spec.md that the built dataset does not
carry (discrepancies D8 and D9).

Usage:
    python tools/check_baseline_ambiguity.py --adlb path/to/adlb.parquet

Requires pyarrow, which is not a dependency of anything else in this repository and
is needed only at step 3 of the method. Read-only. Python 3.10+.

See docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md and
endpoints/01-simple-lab-cfb/comparison.md.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter, defaultdict

COLUMNS = ["USUBJID", "PARAMCD", "AVISIT", "ABLFL", "AVAL", "BASE", "CHG",
           "ANL01FL", "VISIT"]

# Named in ADLB-spec.md's variable table; D8 and D9 assert they are absent.
SPEC_CLAIMS = ["ANRIND", "BNRIND", "BTOXGR"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adlb", required=True, help="path to adlb.parquet")
    ap.add_argument("--baseline-label", default="Baseline",
                    help="AVISIT value for the baseline window (default: Baseline)")
    args = ap.parse_args()

    try:
        import pyarrow.parquet as pq
    except ImportError:
        import _deps
        print(f"error: {_deps.hint('pyarrow')}", file=sys.stderr)
        return 2

    try:
        pf = pq.ParquetFile(args.adlb)
    except Exception as exc:                      # noqa: BLE001 - report and exit
        print(f"error: cannot read {args.adlb}: {exc}", file=sys.stderr)
        return 2

    names = pf.schema_arrow.names
    missing = [c for c in COLUMNS if c not in names]
    if missing:
        print(f"error: expected columns absent: {missing}", file=sys.stderr)
        return 2

    table = pf.read(columns=COLUMNS)
    d = {c: table.column(c).to_pylist() for c in COLUMNS}
    n = table.num_rows

    print("Baseline ambiguity report")
    print(f"file:   {args.adlb}")
    print(f"rows:   {n}   columns: {len(names)}")

    print("\nColumns ADLB-spec.md names but the data does not carry (D8, D9)")
    print("-------------------------------------------------------------")
    for c in SPEC_CLAIMS:
        print(f"  {c:<8} present: {c in names}")
    for c in ("NRIND", "ATOXGR"):
        print(f"  {c:<8} present: {c in names}   (what is carried instead)")

    groups: dict[tuple, list[int]] = defaultdict(list)
    for i in range(n):
        groups[(d["USUBJID"][i], d["PARAMCD"][i])].append(i)

    baseline_rows = Counter()
    no_flag = multi_flag = flag_off_visit = base_mismatch = 0

    for idxs in groups.values():
        bl = [i for i in idxs if d["AVISIT"][i] == args.baseline_label]
        baseline_rows[len(bl)] += 1
        flagged = [i for i in idxs if d["ABLFL"][i] == "Y"]
        if not flagged:
            no_flag += 1
            continue
        if len(flagged) > 1:
            multi_flag += 1
        anchor = flagged[0]
        if d["AVISIT"][anchor] != args.baseline_label:
            flag_off_visit += 1
        for i in idxs:
            if (d["BASE"][i] is not None and d["AVAL"][anchor] is not None
                    and abs(d["BASE"][i] - d["AVAL"][anchor]) > 1e-9):
                base_mismatch += 1
                break

    total = len(groups)
    ambiguous = sum(c for k, c in baseline_rows.items() if k > 1)

    print("\nDoes ABLFL agree with the baseline visit?")
    print("-----------------------------------------")
    print(f"  subject x parameter groups              : {total}")
    print(f"  groups with no ABLFL record             : {no_flag}")
    print(f"  groups with more than one ABLFL         : {multi_flag}")
    print(f"  ABLFL record not at AVISIT={args.baseline_label!r:<10}  : {flag_off_visit}")
    print(f"  BASE != AVAL of the ABLFL record        : {base_mismatch}")

    print(f"\nIs 'AVISIT = {args.baseline_label}' a key?")
    print("-----------------------------------")
    for k in sorted(baseline_rows):
        print(f"  {k} baseline row(s): {baseline_rows[k]} groups")
    pct = 100 * ambiguous / total if total else 0
    print(f"\n  AMBIGUOUS: {ambiguous} of {total} groups ({pct:.1f}%) carry more than one "
          f"record at the baseline visit.")

    if not ambiguous:
        print("\n  The model's slice is a key on this dataset. F12 is latent here.")
        return 0

    differing = 0
    rel: list[float] = []
    pairs = Counter()
    for idxs in groups.values():
        bl = [i for i in idxs if d["AVISIT"][i] == args.baseline_label]
        if len(bl) < 2:
            continue
        pairs[tuple(sorted(str(d["VISIT"][i]) for i in bl))] += 1
        vals = [d["AVAL"][i] for i in bl]
        if all(v is not None for v in vals) and max(vals) - min(vals) > 1e-9:
            differing += 1
        flagged = [i for i in bl if d["ABLFL"][i] == "Y"]
        others = [i for i in bl if d["ABLFL"][i] != "Y"]
        if flagged and others:
            truth, alt = d["AVAL"][flagged[0]], d["AVAL"][others[0]]
            if truth not in (None, 0) and alt is not None:
                rel.append(abs(alt - truth) / abs(truth) * 100)

    print(f"\n  Of the ambiguous groups, the candidate records carry DIFFERENT values in "
          f"{differing} ({100*differing/ambiguous:.1f}%).")
    print("\n  Collected VISIT pairs behind the ambiguity:")
    for v, c in pairs.most_common(5):
        print(f"      {v}: {c}")

    if rel:
        rel.sort()
        print("\n  If the non-flagged candidate were used as BASE, |relative error| in BASE:")
        print(f"      median {statistics.median(rel):.1f}%   mean {statistics.mean(rel):.1f}%"
              f"   p90 {rel[int(0.9*len(rel))]:.1f}%   max {rel[-1]:.1f}%")

    bad = have = 0
    for i in range(n):
        if d["CHG"][i] is None or d["AVAL"][i] is None or d["BASE"][i] is None:
            continue
        have += 1
        if abs(d["CHG"][i] - (d["AVAL"][i] - d["BASE"][i])) > 1e-9:
            bad += 1
    print(f"\n  CHG = AVAL - BASE holds on {have-bad}/{have} rows (violations: {bad}),")
    print("  so any error in BASE passes straight through to CHG.")

    print("\nConclusion: the concept model's baseline slice is not a key on this study.")
    print("See docs/findings/F12-baseline-flag-and-baseline-value-are-disconnected.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
