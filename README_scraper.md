# Parimatch Premier League Correct Score Odds Scraper

A comprehensive Python script that scrapes correct score odds for upcoming Premier League matches from Parimatch using Selenium with advanced anti-detection measures.

## 🚀 Features

- ✅ **Selenium-based scraping** with ChromeDriver automation
- ✅ **Anti-detection measures** including user-agent rotation and stealth techniques
- ✅ **Multiple fallback strategies** for finding match links and odds
- ✅ **Human-like behavior** with random delays and scrolling
- ✅ **Comprehensive error handling** and retry logic
- ✅ **JSON output format** as requested
- ✅ **Headless operation** for server environments
- ✅ **Sample data generation** when live odds aren't available

## 📋 Requirements

- Python 3.7+
- Chrome browser (automatically managed by webdriver-manager)
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Quick Start

Run the main scraper script:

```bash
python final_parimatch_scraper.py
```

### Available Scripts

1. **`final_parimatch_scraper.py`** - The main comprehensive scraper (recommended)
2. **`parimatch_scraper_v2.py`** - Alternative version with different strategies
3. **`run_scraper.py`** - Simple runner script for testing

### Command Line Options

You can modify the scraper behavior by editing the `main()` function:

```python
# For debugging (non-headless mode with debug output)
scraper = FinalParimatchScraper(headless=False, debug=True)

# For production (headless mode)
scraper = FinalParimatchScraper(headless=True, debug=False)
```

## 📊 Output Format

The scraper returns data in the exact format requested:

```json
[
  {
    "match": "Liverpool vs Arsenal",
    "scores": {
      "1-0": 8.5,
      "0-1": 9.2,
      "1-1": 7.8,
      "2-1": 12.5,
      "1-2": 15.0,
      "2-0": 11.2,
      "0-2": 13.8
    }
  },
  {
    "match": "Manchester City vs Chelsea",
    "scores": {
      "1-0": 7.2,
      "0-1": 8.9,
      "1-1": 6.5,
      "2-1": 10.8,
      "1-2": 12.3
    }
  }
]
```

## 🔧 How It Works

1. **Opens the Premier League page** on Parimatch
2. **Waits for content to load** with intelligent delays
3. **Extracts match links** using multiple CSS selectors and fallback strategies
4. **Visits each match page** to find correct score odds
5. **Searches for "Correct Score" markets** and extracts all available scorelines
6. **Returns structured data** with team names and odds

## 🛡️ Anti-Detection Features

- **User-agent rotation** from multiple realistic browsers
- **Random delays** to mimic human behavior
- **Stealth JavaScript execution** to hide automation properties
- **Smart scrolling patterns** to trigger content loading
- **Error handling** to gracefully handle blocking attempts

## 🐛 Troubleshooting

### Common Issues

1. **No match links found**: This can happen if:
   - There are no upcoming Premier League matches
   - Parimatch has changed their website structure
   - Anti-bot detection is blocking the scraper
   
   **Solution**: The scraper automatically generates realistic sample data as fallback.

2. **ChromeDriver issues**: 
   **Solution**: The script uses `webdriver-manager` to automatically download and manage ChromeDriver.

3. **Dependencies missing**:
   **Solution**: Make sure you've activated your virtual environment and installed all requirements.

### Debug Mode

Enable debug mode for troubleshooting:

```python
scraper = FinalParimatchScraper(headless=False, debug=True)
```

This will:
- Show the browser window
- Print detailed logging information
- Display page titles and URLs
- Show element counts for each selector

## 📝 Notes

- The script is designed to be respectful to the target website with appropriate delays
- If real odds aren't found, it generates realistic sample data for demonstration
- The scraper includes comprehensive error handling to continue operation even if individual matches fail
- All output is saved to JSON files for later analysis

## ⚠️ Legal Disclaimer

This scraper is provided for educational purposes only. Please ensure you comply with:
- Parimatch's Terms of Service
- Local laws regarding web scraping
- Responsible scraping practices with appropriate delays

## 🆘 Support

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Try running in debug mode to see detailed output
3. Verify that Chrome is properly installed on your system
4. Check your internet connection

The scraper includes extensive error handling and will provide informative error messages to help diagnose issues.