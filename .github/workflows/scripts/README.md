# EUNL Yearly MSCI World Holdings (via GitHub Actions)

Dieses Repository lädt die vollständigen Holdings des **iShares Core MSCI World UCITS ETF (EUNL/SWDA, ISIN IE00B4L5Y983)** 
und exportiert **pro Jahr ab 2010** den **spätest verfügbaren Stichtag** als CSV.

## Nutzung
1. Gehe oben in den Tab **Actions**.
2. Klicke auf den Workflow **EUNL Yearly Holdings**.
3. Rechts findest du den Button **Run workflow** → einmal anklicken.
4. Warte 2–5 Minuten, bis der Lauf fertig ist.

## Ergebnisse
- Im Repo: `exports/eunl_yearly/`  
  Dort liegt pro Jahr eine CSV-Datei, z. B. `EUNL_holdings_2014-12-19.csv`.
- Als Download: Unter **Actions → letzter Lauf → Artifacts** findest du ein ZIP (`eunl_yearly_exports`).
- Übersicht: `summary/EUNL_yearly_summary.csv` mit Stichtagen und Anzahl Positionen.

## Hinweise
- **EUNL** und **SWDA** sind dasselbe Fondsvehikel (gleiche ISIN). 
  iShares veröffentlicht die Holdings unter SWDA, sie gelten aber auch für EUNL.
- Kleine Lücken in ganz frühen Jahren sind möglich; der Workflow wählt jeweils den spätesten verfügbaren Snapshot pro Jahr.
