"""Step 2 - Compute every KPI that the available data supports and save tables."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data/processed", ROOT / "outputs/tables"


def add_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["vtr"] = df.total_voters / df.total_electors * 100
    df["male_vtr"] = df.male_voters / df.male_electors * 100
    df["female_vtr"] = df.female_voters / df.female_electors * 100
    df["gender_gap_pp"] = df.male_vtr - df.female_vtr              # negative => women out-vote men
    df["elector_gender_ratio"] = df.female_electors / df.male_electors * 1000
    df["female_share_of_votes_pct"] = df.female_voters / df.total_voters * 100
    df["non_voters"] = df.total_electors - df.total_voters
    return df


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    pc = add_kpis(pd.read_csv(PROC / "pc_clean.csv"))
    st = add_kpis(pd.read_csv(PROC / "state_clean.csv"))
    nat_vtr = st.total_voters.sum() / st.total_electors.sum() * 100

    nat = {
        "Total electors": st.total_electors.sum(),
        "Total votes polled": st.total_voters.sum(),
        "Overall VTR %": nat_vtr,
        "Male VTR %": st.male_voters.sum() / st.male_electors.sum() * 100,
        "Female VTR %": st.female_voters.sum() / st.female_electors.sum() * 100,
        "Elector gender ratio (F per 1000 M)": st.female_electors.sum() / st.male_electors.sum() * 1000,
        "Female share of votes %": st.female_voters.sum() / st.total_voters.sum() * 100,
        "Total non-voters": st.non_voters.sum(),
        "PCs analysed": len(pc),
        "PCs where women out-voted men": int((pc.gender_gap_pp < 0).sum()),
        "PC median VTR %": pc.vtr.median(),
        "PC mean VTR %": pc.vtr.mean(),
        "PC std dev of VTR (pp)": pc.vtr.std(),
        "PC coefficient of variation %": pc.vtr.std() / pc.vtr.mean() * 100,
        "Low-turnout PC share (<60%) %": (pc.vtr < 60).mean() * 100,
        "Very-low-turnout PC share (<50%) %": (pc.vtr < 50).mean() * 100,
        "High-turnout PC share (>=75%) %": (pc.vtr >= 75).mean() * 100,
        "Corr(PC size, VTR)": pc.total_electors.corr(pc.vtr),
        "Corr(gender gap, VTR)": pc.gender_gap_pp.corr(pc.vtr),
    }
    pd.Series(nat, name="value").round(2).to_csv(TAB / "01_national_scorecard.csv", header=True)

    st["gap_vs_national_pp"] = st.vtr - nat_vtr
    st["extra_votes_if_at_national_vtr"] = (st.total_electors * nat_vtr / 100 - st.total_voters).clip(lower=0)
    spread = pc.groupby("state").vtr.agg(pc_count="count", pc_vtr_std="std", pc_vtr_min="min", pc_vtr_max="max")
    spread["pc_vtr_range_pp"] = spread.pc_vtr_max - spread.pc_vtr_min
    st = st.merge(spread, left_on="state", right_index=True).sort_values("vtr", ascending=False)
    st["rank"] = range(1, len(st) + 1)
    cols = ["rank", "state", "region", "total_electors", "total_voters", "vtr", "gap_vs_national_pp",
            "male_vtr", "female_vtr", "gender_gap_pp", "elector_gender_ratio", "female_share_of_votes_pct",
            "non_voters", "extra_votes_if_at_national_vtr", "pc_count", "pc_vtr_std", "pc_vtr_range_pp"]
    st[cols].round(2).to_csv(TAB / "02_state_kpis.csv", index=False)

    reg = pc.groupby("region").agg(electors=("total_electors", "sum"), voters=("total_voters", "sum"),
                                   m_e=("male_electors", "sum"), m_v=("male_voters", "sum"),
                                   f_e=("female_electors", "sum"), f_v=("female_voters", "sum"),
                                   pcs=("pc_name", "count"), pc_vtr_std=("vtr", "std"))
    reg["vtr"] = reg.voters / reg.electors * 100
    reg["male_vtr"] = reg.m_v / reg.m_e * 100
    reg["female_vtr"] = reg.f_v / reg.f_e * 100
    reg["gender_gap_pp"] = reg.male_vtr - reg.female_vtr
    reg["elector_gender_ratio"] = reg.f_e / reg.m_e * 1000
    reg[["pcs", "electors", "voters", "vtr", "male_vtr", "female_vtr", "gender_gap_pp",
         "elector_gender_ratio", "pc_vtr_std"]].sort_values("vtr", ascending=False).round(2).to_csv(
        TAB / "03_region_kpis.csv")

    keep = ["state", "pc_name", "total_electors", "vtr", "male_vtr", "female_vtr", "gender_gap_pp", "non_voters"]
    pc.sort_values("vtr")[keep].head(15).round(2).to_csv(TAB / "04_bottom15_pcs.csv", index=False)
    pc.sort_values("vtr", ascending=False)[keep].head(15).round(2).to_csv(TAB / "05_top15_pcs.csv", index=False)
    pc[pc.vtr < 60].sort_values("vtr")[keep].round(2).to_csv(TAB / "06_low_turnout_pcs_below60.csv", index=False)
    pc.sort_values("gender_gap_pp", ascending=False)[keep].head(15).round(2).to_csv(
        TAB / "07_widest_male_lead_pcs.csv", index=False)
    pc.sort_values("gender_gap_pp")[keep].head(15).round(2).to_csv(TAB / "08_widest_female_lead_pcs.csv", index=False)
    pc.sort_values("non_voters", ascending=False)[keep].head(15).round(2).to_csv(
        TAB / "09_most_non_voters_pcs.csv", index=False)

    q1, q3 = pc.vtr.quantile([.25, .75]); iqr = q3 - q1
    out = pc[(pc.vtr < q1 - 1.5 * iqr) | (pc.vtr > q3 + 1.5 * iqr)].sort_values("vtr")
    out[keep].round(2).to_csv(TAB / "10_outlier_pcs_iqr.csv", index=False)
    bands = pd.cut(pc.vtr, [0, 50, 60, 70, 80, 100], labels=["<50", "50-60", "60-70", "70-80", "80+"])
    bt = bands.value_counts().sort_index().rename("pcs").to_frame()
    bt["share_pct"] = (bt.pcs / bt.pcs.sum() * 100).round(1)
    bt.to_csv(TAB / "11_turnout_bands.csv")
    print(pd.Series(nat).round(2).to_string())


if __name__ == "__main__":
    main()
