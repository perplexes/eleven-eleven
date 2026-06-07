# Eleven Eleven

A weekly movement planner built around a longevity idea: there are two weekly
ceilings where the measured benefit maxes out — about **45 MET-hours of aerobic
movement** and **~120 minutes of resistance training** per week. Build your week
with sliders, watch the budget rebalance, and see where you land on the
dose-response curve.

**Live:** https://perplexes.github.io/eleven-eleven/

Named for the **1,111 activities** in its catalogue — the full
[2024 Adult Compendium of Physical Activities](https://pacompendium.com/adult-compendium/),
scraped into SQLite/JSON so every MET value is a real textbook number, not a
guess.

## What it does

- **Movement budget** — MET-hours = intensity × time. Spend your week toward the
  cap and watch a stacked budget bar fill. Lock it at the cap and the sliders
  redistribute to keep the total pinned.
- **Resistance crossover** — strength training is itself aerobic work, so it
  feeds the MET-hour budget (anchored at 5.0 MET, the Compendium's
  squats/deadlift entry).
- **Where you land** — a "you are here" marker on dose-response curves for
  all-cause mortality, cardiovascular disease, type 2 diabetes, depression, and
  cancer.
- **Per-day breakdown, a shuffle of ways to close the gap, and search/sort across
  all 1,111 activities.**

## A note on the curves

The dose-response curves are **approximate** — digitised by dose band from
published meta-analyses, not exact hazard ratios. They show *associations* from
observational cohorts, not proof of causation, and the high-dose tails are
extrapolated from sparse data. "Cancer" especially is a lossy average: colon,
breast and endometrial risk fall most, while melanoma and prostate risk *rise*
with activity. Sources referenced in-app include Zhang 2026 (BJSM), Garcia 2023
(BJSM), Pearce 2022 (JAMA Psychiatry), Aune 2015, Moore 2016, Momma 2022 (BJSM),
and Gordon 2018.

**This is a planning toy, not medical advice.** More movement past the cap is
still healthy — it just stops adding measured longevity benefit in this model.

## Structure

- `index.html` — the whole app (no build step; open it directly)
- `data/compendium.{db,json,js}` — the 1,111-activity dataset
- `scripts/build_compendium.py` — reproducible scraper that regenerates the data

## Rebuilding the data

```sh
python3 scripts/build_compendium.py            # fetch live
PAC_CACHE=/tmp/pac python3 scripts/build_compendium.py   # parse cached html
```
