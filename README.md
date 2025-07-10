# Parimatch Premier League Odds Scraper

A Python script that scrapes correct score odds for upcoming Premier League matches from Parimatch using Selenium with undetected-chromedriver to avoid bot detection.

## Features

- � **Anti-Detection**: Uses undetected-chromedriver to bypass bot detection
- 🔍 **Comprehensive Scraping**: Extracts match links and correct score odds
- 📊 **Structured Output**: Returns data in a clean JSON format
- 🛡️ **Error Handling**: Robust error handling with retries
- 🎯 **Team Recognition**: Automatically extracts team names
- 💾 **Data Persistence**: Saves results to JSON file

## Requirements

- Python 3.7+
- Chrome browser installed
- Dependencies listed in `requirements.txt`

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Chrome browser is installed on your system.

## Usage

### Quick Start

Run the simple test script:
```bash
python run_scraper.py
```

### Advanced Usage

Use the scraper directly in your code:

```python
from parimatch_scraper import ParimatchScraper

# Initialize scraper
scraper = ParimatchScraper(headless=True)

# Scrape all matches
results = scraper.scrape_all_matches()

# Process results
for match in results:
    print(f"Match: {match['match']}")
    for score, odds in match['scores'].items():
        print(f"  {score}: {odds}")
```

### Configuration Options

- `headless=True`: Run browser in headless mode (no GUI)
- `headless=False`: Run browser with GUI (useful for debugging)

## Output Format

The scraper returns a list of dictionaries with this structure:

```json
[
  {
    "match": "Liverpool vs Bournemouth",
    "scores": {
      "1-0": 9.2,
      "1-1": 8.5,
      "2-0": 12.3,
      "2-1": 15.7,
      "0-0": 7.8,
      "0-1": 18.2
    }
  }
]
```

## How It Works

1. **Navigate to Premier League Page**: Opens the Parimatch Premier League pre-match page
2. **Extract Match Links**: Finds all individual match page URLs
3. **Process Each Match**: 
   - Opens each match page
   - Extracts team names
   - Locates correct score betting market
   - Scrapes all available scorelines and odds
4. **Return Structured Data**: Formats results as JSON

## Anti-Detection Features

- Uses undetected-chromedriver
- Realistic user agent strings
- Human-like delays between requests
- Removes automation indicators
- Scrolling and interaction simulation

## Error Handling

The scraper includes comprehensive error handling for:
- Network timeouts
- Element not found errors
- Bot detection
- Page loading issues
- Missing data scenarios

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Compatibility**
   - Solution: Update Chrome browser or let undetected-chromedriver auto-download

2. **No Matches Found**
   - Check if there are upcoming Premier League matches
   - Website might have changed structure
   - Try running with `headless=False` to debug

3. **Bot Detection**
   - The script uses undetected-chromedriver to minimize this
   - Add longer delays between requests if needed
   - Check your IP isn't blocked

4. **Dependencies Missing**
   - Run: `pip install -r requirements.txt`
   - Ensure Chrome browser is installed

### Debug Mode

Run with GUI to see what's happening:
```python
scraper = ParimatchScraper(headless=False)
```

## File Structure

- `parimatch_scraper.py`: Main scraper class and logic
- `run_scraper.py`: Simple test runner script
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Legal Notice

This script is for educational purposes only. Please ensure you comply with:
- Parimatch's Terms of Service
- Your local laws regarding web scraping
- Responsible usage practices

## Contributing

Feel free to submit issues or pull requests to improve the scraper.

## License

This project is provided as-is for educational purposes.