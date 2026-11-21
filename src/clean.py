"""Step 1 - Load raw ECI-style CSVs, convert Indian-format numbers, standardise names, validate."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data/raw", ROOT / "data/processed"

NAME_FIX = {"Chattisgarh": "Chhattisgarh", "Orissa": "Odisha", "NCT OF Delhi": "Delhi"}
REGION = {
    "North": ["Delhi", "Haryana", "Himachal Pradesh", "Jammu & Kashmir", "Punjab", "Rajasthan",
              "Uttarakhand", "Uttar Pradesh", "Chandigarh"],
    "South": ["Andhra Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Puducherry", "Lakshadweep"],
    "East": ["Bihar", "Jharkhand", "Odisha", "West Bengal", "Andaman & Nicobar Islands"],
    "West": ["Goa", "Gujarat", "Maharashtra", "Dadra & Nagar Haveli", "Daman & Diu"],
    "Central": ["Chhattisgarh", "Madhya Pradesh"],
    "North-East": ["Arunachal Pradesh", "Assam", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
                   "Sikkim", "Tripura"],
}
STATE_REGION = {s: r for r, ss in REGION.items() for s in ss}


def to_num(s: pd.Series) -> pd.Series:
    """'1,42,782' -> 142782 ; '70.86%' -> 70.86"""
    return pd.to_numeric(s.astype(str).str.replace(",", "").str.replace("%", ""), errors="coerce")


def load(name: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / name)
    df.columns = [c.strip() for c in df.columns]
    for c in df.columns:
        if c not in ("State", "PC Name", "PC Code"):
            df[c] = to_num(df[c])
    df["State"] = df["State"].str.strip().replace(NAME_FIX)
    df["Region"] = df["State"].map(STATE_REGION)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    return df


def validate(pc: pd.DataFrame, st: pd.DataFrame) -> dict:
    checks = {}
    checks["pc_rows"] = len(pc)
    checks["state_rows"] = len(st)
    checks["missing_values"] = int(pc.isna().sum().sum() + st.isna().sum().sum())
    checks["male_plus_female_equals_total_electors"] = bool(
        ((pc.male_electors + pc.female_electors) == pc.total_electors).all())
    checks["max_gap_reported_vs_recomputed_turnout_pp"] = round(float(
        (pc.total_voters / pc.total_electors * 100 - pc.total_turnout).abs().max()), 4)
    agg = pc.groupby("state")[["total_electors", "total_voters"]].sum()
    j = st.set_index("state")[["total_electors", "total_voters"]].join(agg, rsuffix="_pc")
    checks["pc_sums_match_state_file"] = bool(
        (j.total_electors == j.total_electors_pc).all() and (j.total_voters == j.total_voters_pc).all())
    checks["unmapped_regions"] = int(pc.region.isna().sum())
    return checks


def main():
    pc, st = load("pc-wise-turnout.csv"), load("state-wise-turnout.csv")
    PROC.mkdir(parents=True, exist_ok=True)
    pc.to_csv(PROC / "pc_clean.csv", index=False)
    st.to_csv(PROC / "state_clean.csv", index=False)
    for k, v in validate(pc, st).items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
