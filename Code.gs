// =============================================================================
// COMPLETE FOOTBALL ODDS WEB APP - FIXED VERSION
// =============================================================================

const API_KEY = 'aa0498aa71mshc3f6f0728d1cc2ap14aa0ajsnb7f01ea658a0';
const BASE_URL_ODDS = 'https://api-football-v1.p.rapidapi.com/v3/odds';
const BASE_URL_FIXTURES = 'https://api-football-v1.p.rapidapi.com/v3/fixtures';
const BASE_URL_LEAGUES = 'https://api-football-v1.p.rapidapi.com/v3/leagues';

// =============================================================================
// WEB APP ENTRY POINT
// =============================================================================

function doGet() {
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// =============================================================================
// WEB APP FUNCTIONS
// =============================================================================

function getFixturesForWeb(count = 25) {
  const PARAMS = { next: count.toString() };
  
  try {
    const fixturesData = fetchFixturesData(BASE_URL_FIXTURES, API_KEY, PARAMS);
    
    if (!fixturesData || !fixturesData.response || fixturesData.response.length === 0) {
      return { error: 'No fixtures found' };
    }
    
    const fixtures = fixturesData.response.map(match => {
      const fixture = match.fixture;
      const league = match.league;
      const teams = match.teams;
      
      const matchDate = new Date(fixture.date);
      const dateString = matchDate.toLocaleDateString();
      const timeString = matchDate.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit',
        timeZone: 'UTC'
      });
      
      return {
        id: fixture.id,
        date: dateString,
        time: timeString + ' UTC',
        homeTeam: teams.home.name,
        awayTeam: teams.away.name,
        league: league.name,
        country: league.country,
        venue: fixture.venue ? fixture.venue.name : 'TBD',
        status: fixture.status.long
      };
    });
    
    return {
      success: true,
      count: fixtures.length,
      fixtures: fixtures.slice(0, 20),
      total: fixtures.length
    };
    
  } catch (error) {
    return { error: error.toString() };
  }
}

function getOddsForWeb(fixtureId) {
  const BETS = {
    ANYTIME_GOAL_SCORER: '92',
    CORRECT_SCORE_FIRST_HALF: '31',
    CORRECT_SCORE_SECOND_HALF: '62',
    CLEAN_SHEET_HOME: '27',
    CLEAN_SHEET_AWAY: '28'
  };
  
  try {
    const results = {};
    
    // Get Goal Scorer Data
    try {
      const goalScorerData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, BETS.ANYTIME_GOAL_SCORER);
      if (goalScorerData && goalScorerData.bookmakers) {
        results.goalScorers = extractGoalScorerData(goalScorerData);
      }
    } catch (error) {
      console.log('Goal scorer data not available: ' + error.toString());
    }
    
    // Get First Half Correct Score Data
    try {
      const firstHalfData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, BETS.CORRECT_SCORE_FIRST_HALF);
      if (firstHalfData && firstHalfData.bookmakers) {
        results.firstHalfScores = extractCorrectScoreData(firstHalfData);
      }
    } catch (error) {
      console.log('First half score data not available: ' + error.toString());
    }
    
    // Get Second Half Correct Score Data
    try {
      const secondHalfData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, BETS.CORRECT_SCORE_SECOND_HALF);
      if (secondHalfData && secondHalfData.bookmakers) {
        results.secondHalfScores = extractCorrectScoreData(secondHalfData);
      }
    } catch (error) {
      console.log('Second half score data not available: ' + error.toString());
    }
    
    // Get Clean Sheet Home Data (Bet ID: 27)
    console.log('=== FETCHING HOME CLEAN SHEET (BET ID: 27) ===');
    try {
      const cleanSheetHomeData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, BETS.CLEAN_SHEET_HOME);
      console.log('Home Clean Sheet Raw Data:', JSON.stringify(cleanSheetHomeData, null, 2));
      
      if (cleanSheetHomeData && cleanSheetHomeData.bookmakers && cleanSheetHomeData.bookmakers.length > 0) {
        console.log('Processing Home Clean Sheet data...');
        results.cleanSheetHome = extractCleanSheetData(cleanSheetHomeData);
        console.log('Processed Home Clean Sheet:', JSON.stringify(results.cleanSheetHome, null, 2));
      } else {
        console.log('No Home Clean Sheet bookmakers data available');
        results.cleanSheetHome = [];
      }
    } catch (error) {
      console.log('Home Clean Sheet error:', error.toString());
      results.cleanSheetHome = [];
    }
    
    // Get Clean Sheet Away Data (Bet ID: 28)
    console.log('=== FETCHING AWAY CLEAN SHEET (BET ID: 28) ===');
    try {
      const cleanSheetAwayData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, BETS.CLEAN_SHEET_AWAY);
      console.log('Away Clean Sheet Raw Data:', JSON.stringify(cleanSheetAwayData, null, 2));
      
      if (cleanSheetAwayData && cleanSheetAwayData.bookmakers && cleanSheetAwayData.bookmakers.length > 0) {
        console.log('Processing Away Clean Sheet data...');
        results.cleanSheetAway = extractCleanSheetData(cleanSheetAwayData);
        console.log('Processed Away Clean Sheet:', JSON.stringify(results.cleanSheetAway, null, 2));
      } else {
        console.log('No Away Clean Sheet bookmakers data available');
        results.cleanSheetAway = [];
      }
    } catch (error) {
      console.log('Away Clean Sheet error:', error.toString());
      results.cleanSheetAway = [];
    }
    
    results.fixtureId = fixtureId;
    results.success = true;
    
    // Log final results for debugging
    console.log('=== FINAL RESULTS ===');
    console.log('Clean Sheet Home found:', !!results.cleanSheetHome && results.cleanSheetHome.length > 0);
    console.log('Clean Sheet Away found:', !!results.cleanSheetAway && results.cleanSheetAway.length > 0);
    console.log('Final results object:', JSON.stringify(results, null, 2));
    
    return results;
    
  } catch (error) {
    console.log('Main error in getOddsForWeb: ' + error.toString());
    return { error: error.toString() };
  }
}

function calculateFinalScoresForWeb(fixtureId) {
  try {
    const firstHalfData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, '31');
    const secondHalfData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, '62');
    
    if (!firstHalfData || !secondHalfData) {
      return { error: 'Could not fetch correct score data for this fixture' };
    }
    
    const firstHalfScores = extractCorrectScoreDataForCalculation(firstHalfData);
    const secondHalfScores = extractCorrectScoreDataForCalculation(secondHalfData);
    
    if (!firstHalfScores.length || !secondHalfScores.length) {
      return { error: 'No correct score data available for calculation' };
    }
    
    const finalScores = calculateAllFinalScores(firstHalfScores, secondHalfScores);
    
    const sortedScores = Array.from(finalScores.entries())
      .sort((a, b) => b[1].probability - a[1].probability)
      .slice(0, 20);
    
    const results = {
      success: true,
      fixtureId: fixtureId,
      finalScores: sortedScores.map(([score, data]) => ({
        score: score,
        probability: (data.probability * 100).toFixed(2) + '%',
        odds: data.odds.toFixed(2),
        combinations: data.combinations ? data.combinations.length : 0
      })),
      summary: {
        totalProbability: (Array.from(finalScores.values())
          .reduce((sum, data) => sum + data.probability, 0) * 100).toFixed(2) + '%',
        firstHalfScores: firstHalfScores.length,
        secondHalfScores: secondHalfScores.length
      }
    };
    
    return results;
    
  } catch (error) {
    return { error: error.toString() };
  }
}

function getLeaguesForWeb(season = '2025') {
  const PARAMS = { season: season };
  
  try {
    const leaguesData = fetchLeaguesData(BASE_URL_LEAGUES, API_KEY, PARAMS);
    
    if (!leaguesData || !leaguesData.response || leaguesData.response.length === 0) {
      return { error: 'No leagues found' };
    }
    
    const leaguesByCountry = {};
    
    leaguesData.response.forEach(item => {
      const league = item.league;
      const country = item.country;
      const seasons = item.seasons;
      
      if (!leaguesByCountry[country.name]) {
        leaguesByCountry[country.name] = [];
      }
      
      seasons.forEach(seasonData => {
        if (seasonData.current) {
          leaguesByCountry[country.name].push({
            id: league.id,
            name: league.name,
            type: league.type,
            season: seasonData.year
          });
        }
      });
    });
    
    const topCountries = Object.entries(leaguesByCountry)
      .sort((a, b) => b[1].length - a[1].length)
      .slice(0, 15);
    
    return {
      success: true,
      season: season,
      totalLeagues: leaguesData.response.length,
      topCountries: topCountries.map(([country, leagues]) => ({
        country: country,
        leagueCount: leagues.length,
        leagues: leagues.slice(0, 8)
      }))
    };
    
  } catch (error) {
    return { error: error.toString() };
  }
}

function getFixturesForLeagueWeb(leagueId, count = 25) {
  const PARAMS = { 
    league: leagueId,
    next: count.toString()
  };
  
  try {
    const fixturesData = fetchFixturesData(BASE_URL_FIXTURES, API_KEY, PARAMS);
    
    if (!fixturesData || !fixturesData.response || fixturesData.response.length === 0) {
      return { error: `No fixtures found for league ID ${leagueId}` };
    }
    
    const fixtures = fixturesData.response.map(match => {
      const fixture = match.fixture;
      const league = match.league;
      const teams = match.teams;
      
      const matchDate = new Date(fixture.date);
      const dateString = matchDate.toLocaleDateString();
      const timeString = matchDate.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit',
        timeZone: 'UTC'
      });
      
      return {
        id: fixture.id,
        date: dateString,
        time: timeString + ' UTC',
        homeTeam: teams.home.name,
        awayTeam: teams.away.name,
        league: league.name,
        country: league.country,
        venue: fixture.venue ? fixture.venue.name : 'TBD',
        status: fixture.status.long
      };
    });
    
    return {
      success: true,
      type: 'league',
      leagueId: leagueId,
      leagueName: fixtures.length > 0 ? fixtures[0].league : 'Unknown',
      count: fixtures.length,
      fixtures: fixtures,
      total: fixtures.length
    };
    
  } catch (error) {
    return { error: error.toString() };
  }
}

function getFixturesForDateWeb(date) {
  const PARAMS = { date: date };
  
  try {
    const fixturesData = fetchFixturesData(BASE_URL_FIXTURES, API_KEY, PARAMS);
    
    if (!fixturesData || !fixturesData.response || fixturesData.response.length === 0) {
      return { error: `No fixtures found for ${date}` };
    }
    
    const fixtures = fixturesData.response.map(match => {
      const fixture = match.fixture;
      const league = match.league;
      const teams = match.teams;
      
      const matchDate = new Date(fixture.date);
      const dateString = matchDate.toLocaleDateString();
      const timeString = matchDate.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit',
        timeZone: 'UTC'
      });
      
      return {
        id: fixture.id,
        date: dateString,
        time: timeString + ' UTC',
        homeTeam: teams.home.name,
        awayTeam: teams.away.name,
        league: league.name,
        country: league.country,
        venue: fixture.venue ? fixture.venue.name : 'TBD',
        status: fixture.status.long
      };
    });
    
    return {
      success: true,
      type: 'date',
      searchDate: date,
      count: fixtures.length,
      fixtures: fixtures,
      total: fixtures.length
    };
    
  } catch (error) {
    return { error: error.toString() };
  }
}

// =============================================================================
// CORE API FUNCTIONS
// =============================================================================

function fetchOddsData(baseUrl, apiKey, fixtureId, betId) {
  const url = `${baseUrl}?fixture=${fixtureId}&bet=${betId}`;
  
  const options = {
    'method': 'GET',
    'headers': {
      'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
      'x-rapidapi-key': apiKey
    }
  };
  
  console.log('Fetching odds data from URL: ' + url);
  
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  
  console.log('API Response for bet ' + betId + ':', JSON.stringify(data));
  
  if (data.errors && data.errors.length > 0) {
    throw new Error('API Error: ' + data.errors.join(', '));
  }
  
  return data.response && data.response.length > 0 ? data.response[0] : null;
}

function fetchFixturesData(baseUrl, apiKey, params) {
  const paramString = Object.keys(params)
    .map(key => `${key}=${params[key]}`)
    .join('&');
  
  const url = `${baseUrl}?${paramString}`;
  
  const options = {
    'method': 'GET',
    'headers': {
      'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
      'x-rapidapi-key': apiKey
    }
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  
  if (data.errors && data.errors.length > 0) {
    throw new Error('API Error: ' + data.errors.join(', '));
  }
  
  return data;
}

function fetchLeaguesData(baseUrl, apiKey, params) {
  const paramString = Object.keys(params)
    .map(key => `${key}=${params[key]}`)
    .join('&');
  
  const url = `${baseUrl}?${paramString}`;
  
  const options = {
    'method': 'GET',
    'headers': {
      'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
      'x-rapidapi-key': apiKey
    }
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  
  if (data.errors && data.errors.length > 0) {
    throw new Error('API Error: ' + data.errors.join(', '));
  }
  
  return data;
}



// =============================================================================
// DATA PROCESSING FUNCTIONS
// =============================================================================

function extractGoalScorerData(data) {
  const playersMap = new Map();
  
  data.bookmakers.forEach(bookmaker => {
    if (bookmaker.bets && bookmaker.bets.length > 0) {
      const bet = bookmaker.bets[0];
      if (bet.values) {
        bet.values.forEach(value => {
          if (!playersMap.has(value.value)) {
            playersMap.set(value.value, []);
          }
          playersMap.get(value.value).push({
            bookmaker: bookmaker.name,
            odds: value.odd
          });
        });
      }
    }
  });
  
  const players = Array.from(playersMap.entries()).map(([player, odds]) => ({
    player: player,
    avgOdds: (odds.reduce((sum, odd) => sum + parseFloat(odd.odds), 0) / odds.length).toFixed(2),
    bookmakers: odds.length
  }));
  
  return players.slice(0, 15);
}

function extractCorrectScoreData(data) {
  const scoresMap = new Map();
  
  data.bookmakers.forEach(bookmaker => {
    if (bookmaker.bets && bookmaker.bets.length > 0) {
      const bet = bookmaker.bets[0];
      if (bet.values) {
        bet.values.forEach(value => {
          if (!scoresMap.has(value.value)) {
            scoresMap.set(value.value, []);
          }
          scoresMap.get(value.value).push({
            bookmaker: bookmaker.name,
            odds: value.odd
          });
        });
      }
    }
  });
  
  const scores = Array.from(scoresMap.entries()).map(([score, odds]) => ({
    score: score,
    avgOdds: (odds.reduce((sum, odd) => sum + parseFloat(odd.odds), 0) / odds.length).toFixed(2),
    bookmakers: odds.length
  }));
  
  return scores;
}

// FIXED: Improved clean sheet data extraction with better error handling
function extractCleanSheetData(data) {
  console.log('Extracting clean sheet data from:', JSON.stringify(data));
  
  const cleanSheetMap = new Map();
  
  if (!data.bookmakers || data.bookmakers.length === 0) {
    console.log('No bookmakers data available for clean sheet');
    return [];
  }
  
  data.bookmakers.forEach((bookmaker, bookmakerIndex) => {
    console.log(`Processing bookmaker ${bookmakerIndex + 1}: ${bookmaker.name}`);
    
    if (bookmaker.bets && bookmaker.bets.length > 0) {
      const bet = bookmaker.bets[0];
      console.log('Bet data:', JSON.stringify(bet));
      
      if (bet.values && bet.values.length > 0) {
        bet.values.forEach((value, valueIndex) => {
          console.log(`Processing value ${valueIndex + 1}:`, JSON.stringify(value));
          
          if (!cleanSheetMap.has(value.value)) {
            cleanSheetMap.set(value.value, []);
          }
          cleanSheetMap.get(value.value).push({
            bookmaker: bookmaker.name,
            odds: parseFloat(value.odd)
          });
        });
      } else {
        console.log('No values found in bet for bookmaker:', bookmaker.name);
      }
    } else {
      console.log('No bets found for bookmaker:', bookmaker.name);
    }
  });
  
  console.log('Clean sheet map:', Array.from(cleanSheetMap.entries()));
  
  const cleanSheetOptions = Array.from(cleanSheetMap.entries()).map(([option, odds]) => {
    const avgOdds = (odds.reduce((sum, odd) => sum + odd.odds, 0) / odds.length).toFixed(2);
    return {
      option: option,
      avgOdds: avgOdds,
      bookmakers: odds.length
    };
  });
  
  console.log('Final clean sheet options:', JSON.stringify(cleanSheetOptions));
  
  return cleanSheetOptions;
}

function extractCorrectScoreDataForCalculation(data) {
  const scoreData = [];
  
  data.bookmakers.forEach(bookmaker => {
    if (bookmaker.bets && bookmaker.bets.length > 0) {
      const bet = bookmaker.bets[0];
      if (bet.values) {
        bet.values.forEach(value => {
          const existingScore = scoreData.find(s => s.score === value.value);
          if (existingScore) {
            existingScore.odds.push(parseFloat(value.odd));
          } else {
            scoreData.push({
              score: value.value,
              odds: [parseFloat(value.odd)]
            });
          }
        });
      }
    }
  });
  
  return scoreData.map(item => ({
    score: item.score,
    odds: item.odds.reduce((sum, odd) => sum + odd, 0) / item.odds.length,
    probability: 1 / (item.odds.reduce((sum, odd) => sum + odd, 0) / item.odds.length)
  }));
}

function calculateAllFinalScores(firstHalfData, secondHalfData) {
  const finalScores = new Map();
  
  for (let homeGoals = 0; homeGoals <= 5; homeGoals++) {
    for (let awayGoals = 0; awayGoals <= 5; awayGoals++) {
      const finalScore = `${homeGoals}:${awayGoals}`;
      let totalProbability = 0;
      const combinations = [];
      
      for (let firstHalf of firstHalfData) {
        for (let secondHalf of secondHalfData) {
          const [fh_home, fh_away] = firstHalf.score.split(':').map(Number);
          const [sh_home, sh_away] = secondHalf.score.split(':').map(Number);
          
          if (fh_home + sh_home === homeGoals && fh_away + sh_away === awayGoals) {
            const combinationProb = firstHalf.probability * secondHalf.probability;
            totalProbability += combinationProb;
            combinations.push({
              firstHalf: firstHalf.score,
              secondHalf: secondHalf.score,
              probability: combinationProb
            });
          }
        }
      }
      
      if (totalProbability > 0) {
        finalScores.set(finalScore, {
          probability: totalProbability,
          odds: 1 / totalProbability,
          combinations: combinations
        });
      }
    }
  }
  
  return finalScores;
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function getOrCreateSheet(spreadsheet, sheetName) {
  let sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName);
  }
  return sheet;
}

// =============================================================================
// DEBUGGING FUNCTION - Use this to test clean sheet data directly
// =============================================================================

function testCleanSheetData() {
  const fixtureId = '1338466'; // Your test fixture ID
  
  console.log('=== TESTING CLEAN SHEET DATA ===');
  
  try {
    // Test Home Clean Sheet
    console.log('Testing Home Clean Sheet (Bet ID: 27)');
    const homeData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, '27');
    console.log('Home Clean Sheet Raw Data:', JSON.stringify(homeData, null, 2));
    
    if (homeData && homeData.bookmakers) {
      const homeProcessed = extractCleanSheetData(homeData);
      console.log('Home Clean Sheet Processed:', JSON.stringify(homeProcessed, null, 2));
    }
    
    // Test Away Clean Sheet
    console.log('Testing Away Clean Sheet (Bet ID: 28)');
    const awayData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, '28');
    console.log('Away Clean Sheet Raw Data:', JSON.stringify(awayData, null, 2));
    
    if (awayData && awayData.bookmakers) {
      const awayProcessed = extractCleanSheetData(awayData);
      console.log('Away Clean Sheet Processed:', JSON.stringify(awayProcessed, null, 2));
    }
    
  } catch (error) {
    console.log('Error in testing:', error.toString());
  }
}