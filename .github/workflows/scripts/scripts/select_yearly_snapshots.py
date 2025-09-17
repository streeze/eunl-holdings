#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
import pandas as pd
from dateutil.parser import isoparse

def find_csvs(root: Path, etf: str):
    p = root / 'type=holdings' / 'state=formatted' / f'etf={etf}'
    return sorted(p.glob('asofdate=*.csv')) if p.exists() else []

def parse_asofdate(path: Path):
    try:
        return isoparse(path.stem.split('=')[1]).date()
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--etf', default='SWDA')
    ap.add_argument('--from-year', type=int, default=2010)
    ap.add_argument('--outdir', default='exports/eunl_yearly')
    args = ap.parse_args()

    root = Path(args.root)
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    summary_dir = Path('summary'); summary_dir.mkdir(parents=True, exist_ok=True)

    files = find_csvs(root, args.etf)
    if not files:
        print('No CSVs found. Did the downloader run successfully?', file=sys.stderr); sys.exit(1)

    by_year = {}
    for p in files:
        dt = parse_asofdate(p)
        if dt and dt.year >= args.from_year:
            by_year.setdefault(dt.year, []).append((dt, p))

    rows = []
    for year, items in sorted(by_year.items()):
        items.sort(key=lambda x: x[0])
        dt, p = items[-1]
        df = pd.read_csv(p)
        out_name = outdir / f"EUNL_holdings_{dt.isoformat()}.csv"
        df.to_csv(out_name, index=False)
        rows.append({'year': year, 'asofdate': dt.isoformat(),
                     'export_file': str(out_name),
                     'n_holdings': len(df),
                     'source_csv': str(p)})

    pd.DataFrame(rows).sort_values('year').to_csv(summary_dir / 'EUNL_yearly_summary.csv', index=False)
    print(f"Wrote {len(rows)} yearly files to {outdir}")

if __name__ == '__main__':
    main()
