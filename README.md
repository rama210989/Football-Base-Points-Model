# Premier League Fixtures & Correct Score Odds Scraper

This project scrapes all upcoming Premier League fixtures and their correct score odds from Flashscore, and outputs the results to both the console and a CSV file. It is designed for easy deployment on [Railway](https://railway.app/) but can also be run locally.

## Features
- Scrapes all upcoming Premier League fixtures (home/away teams, event IDs) from Flashscore using Playwright (headless browser).
- For each fixture, fetches correct score odds using the Flashscore odds API.
- Outputs results to the console and to `premier_league_fixtures_and_odds.csv`.
- Robust to JavaScript-rendered content and anti-bot measures.
- No manual intervention required once deployed.

## Files
- `main.py` — Main scraping script.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — For Railway (or any Docker-based) deployment.

## How to Deploy on Railway
1. **Create a new Railway project** and link your GitHub repo containing these files.
2. Railway will automatically build the Docker image and run the script.
3. On each run, the script will scrape the latest fixtures and odds, and output to the console and `premier_league_fixtures_and_odds.csv`.
4. You can manually trigger runs, or (on paid plans) schedule them in the Railway UI.

## How to Run Locally (Optional)
1. Install Python 3.11+ and Docker.
2. Clone this repo.
3. Build and run the Docker image:
   ```sh
   docker build -t pl-odds-scraper .
   docker run --rm pl-odds-scraper
   ```
   Or, to run directly (not recommended, but possible):
   ```sh
   pip install -r requirements.txt
   playwright install --with-deps
   python main.py
   ```

## Output
- Results are printed to the console and saved to `premier_league_fixtures_and_odds.csv` in the project directory.

## Notes
- This script is designed for one-off runs, but can be scheduled in Railway for automation.
- No authentication or API keys are required.
- If Flashscore changes their site structure, minor code updates may be needed.

---

**Questions?** Open an issue or contact the author.