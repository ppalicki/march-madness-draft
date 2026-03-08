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

# (slug, display_name, seed)  — fill in seeds once bracket is set
TEAMS = [
    ("duke",           "Duke",           None),
    ("michigan",       "Michigan",       None),
    ("arizona",        "Arizona",        None),
    ("connecticut",    "Connecticut",    None),
    ("florida",        "Florida",        None),
    ("houston",        "Houston",        None),
    ("michigan-state", "Michigan State", None),
    ("illinois",       "Illinois",       None),
    ("purdue",         "Purdue",         None),
    ("iowa-state",     "Iowa State",     None),
    ("nebraska",       "Nebraska",       None),
    ("texas-tech",     "Texas Tech",     None),
    ("gonzaga",        "Gonzaga",        None),
    ("alabama",        "Alabama",        None),
    ("virginia",       "Virginia",       None),
    ("kansas",         "Kansas",         None),
    ("vanderbilt",     "Vanderbilt",     None),
    ("arkansas",       "Arkansas",       None),
    ("north-carolina", "North Carolina", None),
    ("tennessee",      "Tennessee",      None),
    ("st-johns-ny",    "St. John's",     None),
    ("wisconsin",      "Wisconsin",      None),
    ("louisville",     "Louisville",     None),
    ("kentucky",       "Kentucky",       None),
    ("saint-marys-ca", "Saint Mary's",   None),
    ("brigham-young",  "BYU",            None),
    ("miami-fl",       "Miami (FL)",     None),
    ("villanova",      "Villanova",      None),
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
