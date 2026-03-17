import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

YEAR = 2026
DELAY = 5  # seconds between requests

# (slug, display_name, seed)
TEAMS = [
    # Seed 1
    ("duke",           "Duke",           1),
    ("arizona",        "Arizona",        1),
    ("michigan",       "Michigan",       1),
    ("florida",        "Florida",        1),
    # Seed 2
    ("houston",        "Houston",        2),
    ("connecticut",    "Connecticut",    2),
    ("iowa-state",     "Iowa State",     2),
    ("purdue",         "Purdue",         2),
    # Seed 3
    ("michigan-state", "Michigan State", 3),
    ("illinois",       "Illinois",       3),
    ("gonzaga",        "Gonzaga",        3),
    ("virginia",       "Virginia",       3),
    # Seed 4
    ("nebraska",       "Nebraska",       4),
    ("alabama",        "Alabama",        4),
    ("kansas",         "Kansas",         4),
    ("arkansas",       "Arkansas",       4),
    # Seed 5
    ("vanderbilt",     "Vanderbilt",     5),
    ("st-johns-ny",    "St. John's",     5),
    ("texas-tech",     "Texas Tech",     5),
    ("wisconsin",      "Wisconsin",      5),
    # Seed 6
    ("tennessee",      "Tennessee",      6),
    ("north-carolina", "North Carolina", 6),
    ("louisville",     "Louisville",     6),
    ("brigham-young",  "BYU",            6),
    # Seed 7
    ("kentucky",       "Kentucky",       7),
    ("saint-marys-ca", "Saint Mary's",   7),
    ("miami-fl",       "Miami (FL)",     7),
    ("ucla",           "UCLA",           7),
    # Seed 8
    ("clemson",        "Clemson",        8),
    ("villanova",      "Villanova",      8),
    ("ohio-state",     "Ohio State",     8),
    ("georgia",        "Georgia",        8),
]


def scrape_team(slug: str) -> list[dict]:
    url = f"https://www.sports-reference.com/cbb/schools/{slug}/men/{YEAR}.html"
    print(f"Fetching {url} ...")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Table may be hidden inside an HTML comment
    table = soup.find("table", {"id": "players_per_game"})
    if table is None:
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            inner = BeautifulSoup(comment, "html.parser")
            table = inner.find("table", {"id": "players_per_game"})
            if table:
                break

    if table is None:
        raise RuntimeError(f"[{slug}] Could not find players_per_game table.")

    rows = []
    tbody = table.find("tbody")
    for tr in tbody.find_all("tr"):
        if tr.get("class") and "thead" in tr.get("class"):
            continue

        td_player = tr.find("td", {"data-stat": "name_display"})
        if td_player is None:
            continue

        player_name = td_player.get_text(strip=True)
        if not player_name:
            continue

        def get_stat(stat_id: str) -> str:
            td = tr.find("td", {"data-stat": stat_id})
            return td.get_text(strip=True) if td else ""

        rows.append({
            "Player": player_name,
            "MPG":    get_stat("mp_per_g"),
            "PPG":    get_stat("pts_per_g"),
            "RPG":    get_stat("trb_per_g"),
            "APG":    get_stat("ast_per_g"),
            "SPG":    get_stat("stl_per_g"),
            "BPG":    get_stat("blk_per_g"),
        })

    return rows


def main():
    all_records = []

    for i, (slug, name, seed) in enumerate(TEAMS):
        try:
            rows = scrape_team(slug)
            for row in rows:
                row["Team"] = name
                row["Seed"] = seed
            all_records.extend(rows)
            print(f"  -> {len(rows)} players scraped for {name}")
        except Exception as e:
            print(f"  ERROR scraping {name} ({slug}): {e}")

        if i < len(TEAMS) - 1:
            print(f"Waiting {DELAY}s ...")
            time.sleep(DELAY)

    if not all_records:
        print("No records collected.")
        return

    df = pd.DataFrame(all_records, columns=["Team", "Seed", "Player", "MPG", "PPG", "RPG", "APG", "SPG", "BPG"])

    for col in ["MPG", "PPG", "RPG", "APG", "SPG", "BPG"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    output = "all_teams_stats.csv"
    df.to_csv(output, index=False)
    print(f"\nDone. Saved {len(df)} total players across {df['Team'].nunique()} teams to {output}")


if __name__ == "__main__":
    main()
