import pandas as pd

INPUT = "all_teams_stats.csv"
OUTPUT = "draft_board.csv"
MIN_MPG = 15.0

SEED_GAMES = {
    1: 5.0,
    2: 4.2,
    3: 3.5,
    4: 2.8,
    5: 2.1,
    6: 1.7,
    7: 1.5,
    8: 1.2,
}


def main():
    df = pd.read_csv(INPUT)

    # Drop players below minutes threshold
    df = df[df["MPG"] >= MIN_MPG].copy()

    # Raw score per game
    df["Raw Score"] = df["PPG"] + df["RPG"] + df["APG"] + df["SPG"] + df["BPG"]

    # Map seed to expected games; drop players whose team has no seed set
    df["Seed"] = pd.to_numeric(df["Seed"], errors="coerce")
    missing_seeds = df[df["Seed"].isna()]["Team"].unique()
    if len(missing_seeds):
        print(f"WARNING: No seed set for: {', '.join(missing_seeds)}")
        print("  -> These players will be excluded. Set seeds in get_stats.py and re-run.\n")
        df = df[df["Seed"].notna()]

    df["Seed"] = df["Seed"].astype(int)
    df["Exp Games"] = df["Seed"].map(SEED_GAMES)

    unknown_seeds = df[df["Exp Games"].isna()]["Seed"].unique()
    if len(unknown_seeds):
        print(f"WARNING: No game multiplier for seed(s): {unknown_seeds}. Those players excluded.\n")
        df = df[df["Exp Games"].notna()]

    # Projected tournament total
    df["Proj Total"] = (df["Raw Score"] * df["Exp Games"]).round(1)

    # Tier
    df["Tier"] = pd.cut(
        df["Proj Total"],
        bins=[0, 50, 75, 100, float("inf")],
        labels=["Tier 4", "Tier 3", "Tier 2", "Tier 1"],
        right=False,
    )

    # Build output
    board = (
        df[["Player", "Team", "Seed", "Exp Games", "MPG", "PPG", "RPG", "APG", "SPG", "BPG", "Raw Score", "Proj Total", "Tier"]]
        .rename(columns={"Raw Score": "Raw Score/G", "Exp Games": "Proj Games"})
        .sort_values("Proj Total", ascending=False)
        .reset_index(drop=True)
    )
    board.index += 1  # rank starts at 1
    board.index.name = "Rank"

    board["Raw Score/G"] = board["Raw Score/G"].round(2)

    board.to_csv(OUTPUT)
    print(f"Draft board saved to {OUTPUT}")
    print(f"{len(board)} players ranked\n")
    print(board.head(20).to_string())


if __name__ == "__main__":
    main()
