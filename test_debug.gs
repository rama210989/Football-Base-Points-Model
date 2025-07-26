// =============================================================================
// DEBUG SCRIPT FOR CLEAN SHEET TESTING
// =============================================================================

const API_KEY_DEBUG = 'aa0498aa71mshc3f6f0728d1cc2ap14aa0ajsnb7f01ea658a0';
const BASE_URL_ODDS_DEBUG = 'https://api-football-v1.p.rapidapi.com/v3/odds';

function debugCleanSheetIssue() {
  const fixtureId = '1338466'; // Your test fixture ID
  
  console.log('=== DEBUGGING CLEAN SHEET ISSUE ===');
  console.log('Fixture ID:', fixtureId);
  
  try {
    // Test what bet types are available for this fixture
    console.log('\n1. Testing what bet types are available...');
    const allBetsUrl = `${BASE_URL_ODDS_DEBUG}?fixture=${fixtureId}`;
    const allBetsOptions = {
      'method': 'GET',
      'headers': {
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
        'x-rapidapi-key': API_KEY_DEBUG
      }
    };
    
    const allBetsResponse = UrlFetchApp.fetch(allBetsUrl, allBetsOptions);
    const allBetsData = JSON.parse(allBetsResponse.getContentText());
    
    console.log('All bets response:', JSON.stringify(allBetsData, null, 2));
    
    if (allBetsData.response && allBetsData.response.length > 0) {
      const fixture = allBetsData.response[0];
      console.log('Available bookmakers:', fixture.bookmakers?.length || 0);
      
      if (fixture.bookmakers) {
        fixture.bookmakers.forEach((bookmaker, index) => {
          console.log(`Bookmaker ${index + 1}: ${bookmaker.name}`);
          if (bookmaker.bets) {
            bookmaker.bets.forEach((bet, betIndex) => {
              console.log(`  Bet ${betIndex + 1}: ID=${bet.id}, Name="${bet.name}"`);
            });
          }
        });
      }
    }
    
    console.log('\n2. Testing specific clean sheet bet IDs...');
    
    // Test Home Clean Sheet (Bet ID: 27)
    console.log('\n--- Testing Home Clean Sheet (Bet ID: 27) ---');
    testSpecificBet(fixtureId, '27', 'Home Clean Sheet');
    
    // Test Away Clean Sheet (Bet ID: 28)  
    console.log('\n--- Testing Away Clean Sheet (Bet ID: 28) ---');
    testSpecificBet(fixtureId, '28', 'Away Clean Sheet');
    
    // Test some alternative clean sheet bet IDs that might work
    console.log('\n3. Testing alternative clean sheet bet IDs...');
    const alternativeBetIds = ['29', '30', '31', '32', '33', '34', '35'];
    
    alternativeBetIds.forEach(betId => {
      console.log(`\n--- Testing Bet ID: ${betId} ---`);
      testSpecificBet(fixtureId, betId, `Alternative Bet ${betId}`);
    });
    
  } catch (error) {
    console.log('Error in main debug function:', error.toString());
  }
}

function testSpecificBet(fixtureId, betId, betName) {
  try {
    const url = `${BASE_URL_ODDS_DEBUG}?fixture=${fixtureId}&bet=${betId}`;
    const options = {
      'method': 'GET',
      'headers': {
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
        'x-rapidapi-key': API_KEY_DEBUG
      }
    };
    
    console.log(`Fetching ${betName} from: ${url}`);
    
    const response = UrlFetchApp.fetch(url, options);
    const data = JSON.parse(response.getContentText());
    
    console.log(`${betName} Response:`, JSON.stringify(data, null, 2));
    
    if (data.response && data.response.length > 0) {
      const betData = data.response[0];
      console.log(`${betName} - Found ${betData.bookmakers?.length || 0} bookmakers`);
      
      if (betData.bookmakers && betData.bookmakers.length > 0) {
        betData.bookmakers.forEach((bookmaker, index) => {
          console.log(`  Bookmaker ${index + 1}: ${bookmaker.name}`);
          if (bookmaker.bets && bookmaker.bets.length > 0) {
            bookmaker.bets.forEach((bet, betIndex) => {
              console.log(`    Bet ${betIndex + 1}: ${bet.name} (ID: ${bet.id})`);
              if (bet.values && bet.values.length > 0) {
                bet.values.forEach((value, valueIndex) => {
                  console.log(`      Value ${valueIndex + 1}: ${value.value} = ${value.odd}`);
                });
              } else {
                console.log(`      No values found for this bet`);
              }
            });
          } else {
            console.log(`    No bets found for this bookmaker`);
          }
        });
      } else {
        console.log(`${betName} - No bookmakers found`);
      }
    } else {
      console.log(`${betName} - No data found`);
    }
    
  } catch (error) {
    console.log(`Error testing ${betName}:`, error.toString());
  }
}

// Test with a different fixture ID that might have clean sheet data
function testWithDifferentFixture() {
  console.log('\n=== TESTING WITH DIFFERENT FIXTURE ===');
  
  // Let's try to get some recent fixtures first
  try {
    const fixturesUrl = 'https://api-football-v1.p.rapidapi.com/v3/fixtures?next=10';
    const fixturesOptions = {
      'method': 'GET',
      'headers': {
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
        'x-rapidapi-key': API_KEY_DEBUG
      }
    };
    
    const fixturesResponse = UrlFetchApp.fetch(fixturesUrl, fixturesOptions);
    const fixturesData = JSON.parse(fixturesResponse.getContentText());
    
    if (fixturesData.response && fixturesData.response.length > 0) {
      console.log('Found upcoming fixtures:');
      fixturesData.response.slice(0, 5).forEach((match, index) => {
        const fixture = match.fixture;
        const teams = match.teams;
        console.log(`${index + 1}. Fixture ID: ${fixture.id} - ${teams.home.name} vs ${teams.away.name}`);
        
        // Test clean sheet data for this fixture
        if (index === 0) { // Test only the first fixture to avoid quota issues
          console.log(`\nTesting clean sheet data for fixture ${fixture.id}:`);
          testSpecificBet(fixture.id.toString(), '27', 'Home Clean Sheet');
          testSpecificBet(fixture.id.toString(), '28', 'Away Clean Sheet');
        }
      });
    }
    
  } catch (error) {
    console.log('Error testing with different fixture:', error.toString());
  }
}

// Run this function to get a comprehensive debug report
function runFullDebug() {
  debugCleanSheetIssue();
  Utilities.sleep(2000); // Wait 2 seconds to avoid rate limiting
  testWithDifferentFixture();
}