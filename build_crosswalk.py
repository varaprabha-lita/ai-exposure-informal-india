#!/usr/bin/env python3
"""
Build the SOC-2010 -> ISCO-08 -> NCO-2015 (3-digit) occupation crosswalk that
maps AI Occupational Exposure (AIOE) scores onto India's PLFS occupation codes.

Chain:  AIOE (US SOC-2010, 6-digit)  ->  ISCO-08  ->  3-digit minor group
        (= NCO-2015 three-digit, as used in PLFS 2024).

Inputs (public):
  - AIOE data appendix + Language Modeling file: github.com/AIOE-Data/AIOE
  - SOC-2010 -> ISCO-08 correspondence (ILO), via github.com/Guidowe/occupationcross
Output:
  - aioe_soc.csv                      SOC-2010 -> general AIOE, LM AIOE
  - crosswalk_nco2015_3dig_FINAL.csv  3-digit NCO -> mean AIOE, mean LM AIOE, n_soc

Many SOC -> one NCO: unweighted mean of the constituent AIOE scores.
One SOC -> many NCO: each inherits the source score.
"""
import pandas as pd, pyreadr
from collections import defaultdict

AIOE_DIR = "src_aioe"          # clone of github.com/AIOE-Data/aioe
OCC_DIR  = "src_occ"           # clone of github.com/Guidowe/occupationcross

def minor3(x):
    """ISCO-08 / NCO 3-digit minor group from a code of any length."""
    s = "".join(c for c in str(x).split(".")[0].strip() if c.isdigit())
    return s[:3] if len(s) >= 4 else s.zfill(3)

def main():
    # AIOE: SOC-2010 -> general + language-modelling exposure
    a = pd.read_excel(f"{AIOE_DIR}/AIOE_DataAppendix.xlsx", sheet_name="Appendix A").rename(
        columns={"SOC Code":"soc_code","Occupation Title":"soc_title","AIOE":"aioe"})
    lm = pd.read_excel(f"{AIOE_DIR}/Language Modeling AIOE and AIIE.xlsx", sheet_name="LM AIOE").rename(
        columns={"SOC Code":"soc_code","Language Modeling AIOE":"lm_aioe"})[["soc_code","lm_aioe"]]
    aioe = a.merge(lm, on="soc_code", how="left")[["soc_code","soc_title","aioe","lm_aioe"]]
    aioe.to_csv("aioe_soc.csv", index=False)

    # SOC-2010 -> ISCO-08 (ILO correspondence), reduced to 3-digit
    si = pyreadr.read_r(f"{OCC_DIR}/data/crosstable_soc2010_isco08.rda")["crosstable_soc2010_isco08"]
    si = si.assign(soc=si.SOC.str.strip(), i3=si.ISCO.map(minor3))
    soc2i3 = defaultdict(set)
    for r in si.itertuples():
        soc2i3[r.soc].add(r.i3)

    # aggregate AIOE to 3-digit occupation groups
    acc = defaultdict(lambda: {"a": [], "l": []})
    for r in aioe.itertuples():
        for i3 in soc2i3.get(r.soc_code.strip(), []):
            acc[i3]["a"].append(r.aioe); acc[i3]["l"].append(r.lm_aioe)

    def mean(v):
        v = [x for x in v if pd.notna(x)]
        return round(sum(v)/len(v), 6) if v else None

    rows = [[k, mean(v["a"]), mean(v["l"]), len(v["a"])] for k, v in sorted(acc.items())]
    xw = pd.DataFrame(rows, columns=["nco2015_3dig","aioe","lm_aioe","n_soc"])
    xw.to_csv("crosswalk_nco2015_3dig_FINAL.csv", index=False)
    print(f"{len(aioe)} SOC occupations -> {len(xw)} three-digit NCO groups")

if __name__ == "__main__":
    main()
