# IOT Ticker File Organization Summary

## Current File Structure (T1 Audit Completed)

### Core AHF Files
- **A.yaml**: Materials (T1 verbatim quotes from Ex.99.1 + 10-Q)
- **B.yaml**: Decision (Horizon + ΔIRR + KPI×2 with T1 confirmed data)
- **C.yaml**: Counter-evidence (3 fixed tests + TW calculation log)

### T1 Audit Results
- **facts.md**: T1 verbatim quotes (≤40 words, Ex.99.1 + 10-Q sources)
- **triage.json**: CONFIRMED T1 data + UNCERTAIN gaps
- **impact_cards.json**: ALPHA5/ALPHA3 calculation cards
- **ahf_matrix_t1_confirmed.json**: T1 confirmed AHF matrix with star ratings

### Supporting Files
- **forensic.json**: Updated with T1 audit completion status
- **backlog.md**: Non-T1 data pool (U/Lead one-table)
- **conclusion_t1_audit.md**: One-liner conclusion + audit summary

## Removed Redundant Files
- ~~ahf_matrix.json~~ (old data, replaced by ahf_matrix_t1_confirmed.json)
- ~~alpha5.json~~ (old data_gap, replaced by T1 confirmed calculation)
- ~~alpha3.json~~ (old data_gap, confirmed as data_gap)
- ~~q_baseline.json~~ (old Q3 2025 data)
- ~~t1_discovery.json~~ (old discovery data)
- ~~tripwire.json~~ (old data_gap, replaced by TW calculation in C.yaml)
- ~~contract_balances.json~~ (old data_gap, replaced by T1 confirmed data)

## Key T1 Audit Results
- **ALPHA5**: OpEx ≈ $240,595k (T1 confirmed)
- **ALPHA3**: data_gap (single segment)
- **Coverage**: 10.7 months (Gate < 11)
- **CL q/q**: +4.9% (+5% TW not reached)
- **TW Hit**: false (CL<+5% AND coverage<11)

## File Organization Status: ✅ COMPLETED
- All redundant files removed
- T1 confirmed data properly organized
- File structure clean and consistent
- Ready for next AHF snapshot
