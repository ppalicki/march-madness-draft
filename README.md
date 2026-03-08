# March Madness Draft Stats Scraper

Scrapes per-game player stats for all 28 tournament teams from [Sports Reference CBB](https://www.sports-reference.com/cbb) and saves them to a CSV for use in a draft.

## Output

`all_teams_stats.csv` — one row per player with the following columns:

| Column | Description |
|--------|-------------|
| Team | Team display name |
| Seed | Tournament seed (fill in manually) |
| Player | Player name |
| MPG | Minutes per game |
| PPG | Points per game |
| RPG | Rebounds per game |
| APG | Assists per game |
| SPG | Steals per game |
| BPG | Blocks per game |

## Requirements

```
pip install requests beautifulsoup4 pandas
```

## Usage

```
python get_stats.py
```

Scrapes all 28 teams in sequence with a **5-second delay** between requests to avoid rate limiting by Sports Reference. Runtime is approximately 2.5 minutes.

## Adding Seeds

The `Seed` column is set to `None` by default. To add seeds, edit the `TEAMS` list in `get_stats.py` and replace `None` with the seed number for each team:

```python
("duke", "Duke", 1),
("kentucky", "Kentucky", 4),
```

Then re-run the script to regenerate the CSV with seeds populated.

## Adding or Changing Teams

Edit the `TEAMS` list in `get_stats.py`. Each entry is a tuple of:

```python
("sports-reference-slug", "Display Name", seed_or_None)
```

The slug is the path segment from the team's Sports Reference URL:
`https://www.sports-reference.com/cbb/schools/{slug}/men/2026.html`
