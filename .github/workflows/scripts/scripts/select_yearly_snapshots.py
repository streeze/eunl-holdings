#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import pandas as pd
from dateutil.parser import isoparse

# Input directory structure produced by talsan/ishares downloader:
# {root}/type=holdings/state=formatted/etf=SWDA/asofdate=YYYY-MM-DD.csv

def find_csvs(root: Path, etf: str) -> list[Path]:
    patt = root / 'type=holdings' / 'state=formatted' / f'etf={etf}'
    if not patt.exists():
        return []
    return sorted(patt.glob('asofdate=*.csv'))

def parse_asofdate(p: Path):
    # filename: asofdate=YYYY-MM-DD.csv
    name = p.stem  # asofdate=YYYY-MM-DD
    try:
        date_str = name.split('=')[1]
        dt = isoparse(date_str).date()
        return dt
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True, help='Root path where ishares downloader wrote files (e.g., data/ishares)')
    ap.add_argument('--etf', default='SWDA', help='ETF code inside ishares dataset (SWDA for EUNL/SWDA)')
    ap.add_argument('--from-year', type=int, default=2010)
    ap.add_argument('--outdir', default='exports/eunl_yearly')
    args = ap.parse_args()

    root = Path(args.root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary_dir = Path('summary')
    summary_dir.mkdir(parents=True, exist_ok=True)

    files = find_csvs(root, args.etf)
    if not files:
        print('No CSVs found. Did the downloader run successfully?', file=sys.stderr)
        sys.exit(1)

    # Map: year -> list[(date, path)]
    by_year = {}
    for p in files:
        dt = parse_asofdate(p)
        if not dt:
            continue
        if dt.year < args.from_year:
            continue
        by_year.setdefault(dt.year, []).append((dt, p))

    rows = []
    for year, items in sorted(by_year.items()):
        # pick latest date within the year
        items.sort(key=lambda x: x[0])
        dt, p = items[-1]
        # Load CSV to count rows and basic checks
        df = pd.read_csv(p)
        # Some files can have weight columns named slightly differently; try to normalize
        weight_cols = [c for c in df.columns if c.lower() in {'weight', 'weight_percent', 'weighting', 'weight (%)', 'fund weight'}]
        weight_sum = None
        if weight_cols:
            try:
                weight_sum = pd.to_numeric(df[weight_cols[0]], errors='coerce').sum()
            except Exception:
                weight_sum = None
        n_missing_isin = df['isin'].isna().sum() if 'isin' in df.columns else None
        n_rows = len(df)

        # Write file as EUNL_YYYY-MM-DD.csv (same holdings as SWDA)
        out_name = outdir / f"EUNL_holdings_{dt.isoformat()}.csv"
        df.to_csv(out_name, index=False)

        rows.append({
            'year': year,
            'asofdate': dt.isoformat(),
            'export_file': str(out_name),
            'n_holdings': n_rows,
            'weight_sum_raw': weight_sum,
            'missing_isin': n_missing_isin,
            'source_csv': str(p)
        })

    summary = pd.DataFrame(rows).sort_values(['year'])
    summary_path = summary_dir / 'EUNL_yearly_summary.csv'
    summary.to_csv(summary_path, index=False)
    print(f"Wrote {len(summary)} yearly files to {outdir}")
    print(f"Summary: {summary_path}")

if __name__ == '__main__':
    main()
