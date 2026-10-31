#!/usr/bin/env python3
"""
Estimate the survey-weighted linear probability models of informal employment on
AI exposure (Table II). Run analysis.py first to produce analysis_workers.csv.gz.

  informal_i = beta * AIOE_o(i) + x_i'gamma + state FE + e_i

Survey-weighted (WLS); SEs clustered by occupation.
"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf

def main():
    a = pd.read_csv("analysis_workers.csv.gz", dtype={"ST":str,"nco3":str})
    a["aioe_z"] = (a.aioe - a.aioe.mean()) / a.aioe.std()
    a["lm_z"]   = (a.lm_aioe - a.lm_aioe.mean()) / a.lm_aioe.std()
    a["age2"]   = a.age**2
    d = a.dropna(subset=["informal","aioe_z","age","edu_years","female","urban","ST"]).copy()

    for name, x in [("General AIOE","aioe_z"), ("Language-modelling AIOE","lm_z")]:
        m = smf.wls(f"informal ~ {x} + age + age2 + female + edu_years + urban + C(ST)",
                    data=d, weights=d.w).fit(cov_type="cluster",
                    cov_kwds={"groups": d.nco3})
        print(f"{name}: beta={m.params[x]:+.4f}  SE={m.bse[x]:.4f}  "
              f"p={m.pvalues[x]:.3g}  N={int(m.nobs):,}")

if __name__ == "__main__":
    main()
