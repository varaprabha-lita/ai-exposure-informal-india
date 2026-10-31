#!/usr/bin/env python3
"""
Robustness checks (Table III): alternative informality definitions and
subsamples, including excluding agriculture. Run analysis.py first.
"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf

def main():
    a = pd.read_csv("analysis_workers.csv.gz",
                    dtype={"ST":str,"nco3":str,"PAS":str,"JOB_PAS":str,
                           "ETYP_PAS":str,"SSEC_PAS":str})
    a["aioe_z"] = (a.aioe - a.aioe.mean()) / a.aioe.std()
    a["age2"]   = a.age**2
    formal_etyp = {"05","06","07","08","10","11"}
    a["informal_contract"] = np.where(a.PAS.isin(["31","41","51"]),
                                       (a.JOB_PAS == "1").astype(float), np.nan)
    a["informal_sector"]   = (~a.ETYP_PAS.isin(formal_etyp)).astype(int)
    a["wage"] = a.PAS.isin(["31","41","51"])
    a["agri"] = a.nco3.str.startswith("6") | a.nco3.str.startswith("92")

    def reg(df, dep):
        df = df.dropna(subset=[dep,"aioe_z","age","edu_years","female","urban","ST"])
        m = smf.wls(f"{dep} ~ aioe_z + age + age2 + female + edu_years + urban + C(ST)",
                    data=df, weights=df.w).fit(cov_type="cluster",
                    cov_kwds={"groups": df.nco3})
        return m.params["aioe_z"], m.bse["aioe_z"], m.pvalues["aioe_z"], int(m.nobs)

    specs = [
        ("Baseline (social security + sector)", a, "informal"),
        ("Alt.: no written contract",          a[a.wage], "informal_contract"),
        ("Alt.: informal sector (enterprise)", a, "informal_sector"),
        ("Baseline, wage workers only",        a[a.wage], "informal"),
        ("Baseline, excluding agriculture",    a[~a.agri], "informal"),
    ]
    for label, df, dep in specs:
        b, se, p, n = reg(df, dep)
        print(f"{label:40s}  beta={b:+.4f}  SE={se:.4f}  p={p:.3g}  N={n:,}")

if __name__ == "__main__":
    main()
