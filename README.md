# AI Exposure and Informal Employment in India

Replication materials for the paper *"AI Exposure and Informal Employment in
India: Evidence from the Periodic Labour Force Survey."*

This repository contains the occupation crosswalk and analysis code used to map
occupation-level AI Occupational Exposure (AIOE) scores onto India's Periodic
Labour Force Survey (PLFS) and to estimate the relationship between AI exposure
and informal employment.

## Contents

| File | Description |
| --- | --- |
| `crosswalk_nco2015_3dig_FINAL.csv` | Final crosswalk: three-digit NCO-2015 occupation code → general AIOE and language-modelling AIOE exposure scores. |
| `aioe_soc.csv` | AIOE exposure scores by six-digit US SOC-2010 occupation code (source data). |
| `build_crosswalk.py` | Builds the SOC-2010 → ISCO-08 → NCO-2015 (3-digit) crosswalk. |
| `analysis.py` | Merges exposure scores onto PLFS, constructs the informality measure, and produces the descriptive tables. |
| `regress.py` | Estimates the survey-weighted linear probability models (Table II). |
| `robust.py` | Robustness checks across informality definitions and subsamples (Table III). |

## Data

The PLFS January–December 2024 unit-level data are **not** included here. They
are publicly available from the MoSPI Microdata Portal:
https://microdata.gov.in (person-level file `cperv1`; registration required).

The AIOE source data are from Felten, Raj and Seamans (2021),
https://github.com/AIOE-Data/AIOE.

## Occupation crosswalk

AIOE is published at six-digit US SOC-2010; PLFS codes occupation at three-digit
NCO-2015 (ISCO-08 based). The crosswalk bridges them via ISCO-08:
SOC-2010 → ISCO-08 → three-digit minor group (= NCO-2015 3-digit). It assigns an
exposure score to 126 three-digit occupation groups and covers 100% of employed
PLFS workers by sampling weight. All concordances are drawn from published
sources (ILO SOC↔ISCO-08 correspondence).

## Requirements

Python 3 with `pandas`, `numpy`, `statsmodels`, `matplotlib`, `openpyxl`,
`pyreadr`.

## Citation

If you use these materials, please cite the paper and this repository.

## Data and usage notes

AIOE measures *potential* occupational exposure to AI; it is agnostic as to
whether AI substitutes for or complements a worker. The analysis is
cross-sectional and identifies association, not causation.
