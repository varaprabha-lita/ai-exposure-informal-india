#!/usr/bin/env python3
"""
Merge AIOE exposure onto PLFS 2024 workers, build the informality measure, and
produce the descriptive tables (Table I and the exposure-decile gradient).

Requires the PLFS Jan-Dec 2024 person file `cperv1.csv` (not distributed here):
obtain it from the MoSPI Microdata Portal, https://microdata.gov.in
Also requires crosswalk_nco2015_3dig_FINAL.csv (from build_crosswalk.py).
"""
import pandas as pd, numpy as np

PLFS = "cperv1.csv"   # PLFS 2024 person file from MoSPI

def m3(x):
    s = "".join(c for c in str(x).split(".")[0].strip() if c.isdigit())
    return s[:3] if len(s) >= 4 else s.zfill(3)

def load():
    xw = pd.read_csv("crosswalk_nco2015_3dig_FINAL.csv", dtype={"nco2015_3dig": str})
    cols = ["OCU_PAS","PAS","ETYP_PAS","JOB_PAS","SSEC_PAS","ERN_REG",
            "MULT","SEC","ST","AGE","SEX","GEDU_LVL"]
    pl = pd.read_csv(PLFS, usecols=cols, dtype=str, low_memory=False)
    # employed under usual principal activity status
    emp = pl[pl.PAS.isin(["11","12","21","31","41","51"])].copy()
    emp["nco3"]   = emp.OCU_PAS.map(m3)
    emp["w"]      = pd.to_numeric(emp.MULT, errors="coerce")
    emp["age"]    = pd.to_numeric(emp.AGE, errors="coerce")
    emp["female"] = (emp.SEX == "2").astype(int)
    emp["urban"]  = (emp.SEC == "2").astype(int)
    edu = {"01":0,"02":2,"03":2,"04":2,"05":3,"06":5,"07":8,
           "08":10,"10":12,"11":13,"12":15,"13":17}
    emp["edu_years"] = emp.GEDU_LVL.map(edu)
    emp = emp.merge(xw[["nco2015_3dig","aioe","lm_aioe"]],
                    left_on="nco3", right_on="nco2015_3dig", how="left")
    # informality: NOT (has social security OR formal-sector enterprise)
    formal_etyp = {"05","06","07","08","10","11"}
    emp["has_socsec"]     = emp.SSEC_PAS.isin(["1","2","3","4","5","6","7"])
    emp["formal_sector"]  = emp.ETYP_PAS.isin(formal_etyp)
    emp["informal"]       = (~(emp.has_socsec | emp.formal_sector)).astype(int)
    emp["wage_worker"]    = emp.PAS.isin(["31","41","51"])
    return emp

def wmean(d, col): return np.average(d[col], weights=d.w)

def main():
    emp = load()
    a = emp.dropna(subset=["aioe"]).copy()
    tot = emp.w.sum()
    print(f"Employed workers: {len(emp):,} | exposure coverage (wt): "
          f"{100*a.w.sum()/tot:.1f}% | informal (wt): "
          f"{100*(emp.w*emp.informal).sum()/tot:.1f}%")

    # Table I: exposure by informality
    t1 = a.groupby("informal").apply(lambda d: pd.Series({
        "share": 100*d.w.sum()/a.w.sum(),
        "mean_AIOE": wmean(d,"aioe"),
        "mean_LM_AIOE": wmean(d,"lm_aioe")})).reset_index()
    t1["informal"] = t1.informal.map({0:"Formal",1:"Informal"})
    t1.to_csv("table1_exposure_by_informality.csv", index=False)
    print(t1.to_string(index=False))

    # exposure-decile gradient
    a["decile"] = pd.qcut(a.aioe, 10, labels=False, duplicates="drop") + 1
    t2 = a.groupby("decile").apply(lambda d: pd.Series({
        "mean_AIOE": wmean(d,"aioe"),
        "informal_share": 100*np.average(d.informal, weights=d.w)})).reset_index()
    t2.to_csv("table2_informal_by_exposure_decile.csv", index=False)
    a.to_csv("analysis_workers.csv.gz", index=False, compression="gzip")

if __name__ == "__main__":
    main()
