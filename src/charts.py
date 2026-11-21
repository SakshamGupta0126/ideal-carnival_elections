"""Step 3 - Build charts from the KPI tables / cleaned data."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/charts"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = pd.read_csv(ROOT / "outputs/tables/02_state_kpis.csv")
    pc = pd.read_csv(ROOT / "data/processed/pc_clean.csv")
    pc["vtr"] = pc.total_voters / pc.total_electors * 100
    pc["gap"] = pc.male_voters / pc.male_electors * 100 - pc.female_voters / pc.female_electors * 100
    nat = st.total_voters.sum() / st.total_electors.sum() * 100

    s = st.sort_values("vtr")
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.barh(s.state, s.vtr, color=["#c0392b" if v < nat else "#2e86c1" for v in s.vtr])
    ax.axvline(nat, color="k", ls="--", lw=1); ax.text(nat + .5, 0, f"National {nat:.1f}%", fontsize=8)
    ax.set_xlabel("Voter Turnout Ratio (%)"); ax.set_title("State / UT turnout vs national (blue = above)")
    fig.tight_layout(); fig.savefig(OUT / "01_state_vtr.png"); plt.close(fig)

    s = st.sort_values("gender_gap_pp")
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.barh(s.state, s.gender_gap_pp, color=["#8e44ad" if v < 0 else "#e67e22" for v in s.gender_gap_pp])
    ax.axvline(0, color="k", lw=1)
    ax.set_xlabel("Male VTR - Female VTR (pp)  |  negative = women out-vote men")
    ax.set_title("Gender turnout gap by state / UT")
    fig.tight_layout(); fig.savefig(OUT / "02_gender_gap_state.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(pc.vtr, bins=30, color="#2e86c1", edgecolor="white")
    ax.axvline(pc.vtr.median(), color="k", ls="--", lw=1, label=f"Median {pc.vtr.median():.1f}%")
    ax.axvline(60, color="#c0392b", ls=":", lw=1, label="60% line")
    ax.set_xlabel("PC turnout (%)"); ax.set_ylabel("No. of constituencies")
    ax.set_title("Distribution of constituency turnout (543 PCs)"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "03_pc_distribution.png"); plt.close(fig)

    order = pc.groupby("state").vtr.median().sort_values().index
    big = [x for x in order if (pc.state == x).sum() >= 5]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.boxplot([pc[pc.state == x].vtr for x in big], vert=False, tick_labels=big)
    ax.set_xlabel("PC turnout (%)"); ax.set_title("Within-state spread of turnout (states with 5+ PCs)")
    fig.tight_layout(); fig.savefig(OUT / "04_within_state_spread.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(pc.total_electors / 1e5, pc.vtr, s=10, alpha=.6, color="#2e86c1")
    ax.set_xlabel("Registered electors (lakh)"); ax.set_ylabel("Turnout (%)")
    ax.set_title(f"Constituency size vs turnout (r = {pc.total_electors.corr(pc.vtr):.2f})")
    fig.tight_layout(); fig.savefig(OUT / "05_size_vs_turnout.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(pc.vtr, pc.gap, s=10, alpha=.6, color="#8e44ad"); ax.axhline(0, color="k", lw=1)
    ax.set_xlabel("PC turnout (%)"); ax.set_ylabel("Gender gap (pp)")
    ax.set_title(f"Gender gap vs turnout by constituency (r = {pc.gap.corr(pc.vtr):.2f})")
    fig.tight_layout(); fig.savefig(OUT / "06_gap_vs_turnout.png"); plt.close(fig)

    r = pd.read_csv(ROOT / "outputs/tables/03_region_kpis.csv").sort_values("vtr")
    x = list(range(len(r))); w = .38
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([i - w / 2 for i in x], r.male_vtr, w, label="Male", color="#2e86c1")
    ax.bar([i + w / 2 for i in x], r.female_vtr, w, label="Female", color="#8e44ad")
    ax.set_xticks(x); ax.set_xticklabels(r.region); ax.set_ylim(50, 80); ax.set_ylabel("VTR (%)")
    ax.set_title("Turnout by region and gender"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "07_region_gender.png"); plt.close(fig)
    print("charts saved")


if __name__ == "__main__":
    main()
