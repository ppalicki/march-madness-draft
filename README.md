# March Madness Draft Stats Scraper

Two-script pipeline that scrapes per-game player stats for all 28 tournament teams from [Sports Reference CBB](https://www.sports-reference.com/cbb), scores each player using a seed-weighted projection model, and outputs a ranked draft board.

## Scripts

### `get_stats.py` — Scraper
Fetches per-game stats for all 28 teams and saves them to `all_teams_stats.csv`.

### `scoring_model.py` — Scoring Model
Reads `all_teams_stats.csv`, scores every eligible player, and outputs a ranked `draft_board.csv`.

---

## Requirements

```
pip install requests beautifulsoup4 pandas
```

---

## Usage

**Step 1 — Scrape stats:**
```
python get_stats.py
```
Scrapes all 28 teams with a 5-second delay between requests (~2.5 min total). Output: `all_teams_stats.csv`.

**Step 2 — Generate draft board:**
```
python scoring_model.py
```
Output: `draft_board.csv` sorted by projected tournament total, highest to lowest.

---

## Scoring Model

Players must average **15+ minutes per game** to be included.

**Raw Score/G** = PPG + RPG + APG + SPG + BPG

**Projected Total** = Raw Score/G × Expected Tournament Games

Expected games by seed:

| Seed | Projected Games |
|------|----------------|
| 1 | 5.0 |
| 2 | 4.2 |
| 3 | 3.5 |
| 4 | 2.8 |
| 5 | 2.1 |
| 6 | 1.7 |
| 7 | 1.5 |

---

## Output Files

### `all_teams_stats.csv`

| Column | Description |
|--------|-------------|
| Team | Team display name |
| Seed | Tournament seed |
| Player | Player name |
| MPG | Minutes per game |
| PPG | Points per game |
| RPG | Rebounds per game |
| APG | Assists per game |
| SPG | Steals per game |
| BPG | Blocks per game |

### `draft_board.csv`

| Column | Description |
|--------|-------------|
| Rank | Overall draft rank |
| Player | Player name |
| Team | Team display name |
| Seed | Tournament seed |
| Proj Games | Expected tournament games |
| MPG | Minutes per game |
| PPG | Points per game |
| RPG | Rebounds per game |
| APG | Assists per game |
| SPG | Steals per game |
| BPG | Blocks per game |
| Raw Score/G | Sum of all stats per game |
| Proj Total | Projected tournament total (primary sort) |

---

## Adding or Changing Teams

Edit the `TEAMS` list in `get_stats.py`. Each entry is a tuple of:

```python
("sports-reference-slug", "Display Name", seed)
```

The slug is the path segment from the team's Sports Reference URL:
`https://www.sports-reference.com/cbb/schools/{slug}/men/2026.html`
