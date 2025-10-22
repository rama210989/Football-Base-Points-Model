// =============================================================================
// FOCUSED DEBUG FOR BET IDs 27 AND 28 (CLEAN SHEETS)
// =============================================================================

function debugSpecificCleanSheetBets() {
  const fixtureId = '1338466';
  const API_KEY = 'aa0498aa71mshc3f6f0728d1cc2ap14aa0ajsnb7f01ea658a0';
  const BASE_URL_ODDS = 'https://api-football-v1.p.rapidapi.com/v3/odds';
  
  console.log('=== DEBUGGING CLEAN SHEET BET IDs 27 & 28 ===');
  console.log('Fixture ID:', fixtureId);
  
  // Test Bet ID 27 (Home Clean Sheet)
  console.log('\n--- TESTING BET ID 27 (HOME CLEAN SHEET) ---');
  testBetId(fixtureId, '27', 'Home Clean Sheet', API_KEY, BASE_URL_ODDS);
  
  // Test Bet ID 28 (Away Clean Sheet)
  console.log('\n--- TESTING BET ID 28 (AWAY CLEAN SHEET) ---');
  testBetId(fixtureId, '28', 'Away Clean Sheet', API_KEY, BASE_URL_ODDS);
}

function testBetId(fixtureId, betId, betName, apiKey, baseUrl) {
  try {
    const url = `${baseUrl}?fixture=${fixtureId}&bet=${betId}`;
    
    console.log(`\n1. Fetching ${betName} from URL: ${url}`);
    
    const options = {
      'method': 'GET',
      'headers': {
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com',
        'x-rapidapi-key': apiKey
      }
    };
    
    const response = UrlFetchApp.fetch(url, options);
    const data = JSON.parse(response.getContentText());
    
    console.log(`\n2. Raw API Response for ${betName}:`);
    console.log(JSON.stringify(data, null, 2));
    
    // Check if there are errors
    if (data.errors && data.errors.length > 0) {
      console.log(`\n❌ API Errors for ${betName}:`, data.errors);
      return;
    }
    
    // Check if there's response data
    if (!data.response || data.response.length === 0) {
      console.log(`\n❌ No response data for ${betName}`);
      return;
    }
    
    const betData = data.response[0];
    console.log(`\n3. Processing ${betName} data...`);
    console.log(`   - Fixture ID: ${betData.fixture?.id}`);
    console.log(`   - League: ${betData.league?.name}`);
    console.log(`   - Bookmakers count: ${betData.bookmakers?.length || 0}`);
    
    if (!betData.bookmakers || betData.bookmakers.length === 0) {
      console.log(`\n❌ No bookmakers data for ${betName}`);
      return;
    }
    
    // Analyze each bookmaker
    betData.bookmakers.forEach((bookmaker, bookmakerIndex) => {
      console.log(`\n   Bookmaker ${bookmakerIndex + 1}: ${bookmaker.name}`);
      console.log(`   - Bets count: ${bookmaker.bets?.length || 0}`);
      
      if (bookmaker.bets && bookmaker.bets.length > 0) {
        bookmaker.bets.forEach((bet, betIndex) => {
          console.log(`     Bet ${betIndex + 1}:`);
          console.log(`     - ID: ${bet.id}`);
          console.log(`     - Name: ${bet.name}`);
          console.log(`     - Values count: ${bet.values?.length || 0}`);
          
          if (bet.values && bet.values.length > 0) {
            bet.values.forEach((value, valueIndex) => {
              console.log(`       Value ${valueIndex + 1}: "${value.value}" = ${value.odd}`);
            });
          } else {
            console.log(`       ❌ No values found for this bet`);
          }
        });
      } else {
        console.log(`     ❌ No bets found for this bookmaker`);
      }
    });
    
    // Test the extractCleanSheetData function
    console.log(`\n4. Testing extractCleanSheetData function for ${betName}...`);
    try {
      const processedData = extractCleanSheetData(betData);
      console.log(`   Processed data:`, JSON.stringify(processedData, null, 2));
      
      if (processedData && processedData.length > 0) {
        console.log(`   ✅ Successfully processed ${processedData.length} clean sheet options`);
      } else {
        console.log(`   ❌ extractCleanSheetData returned empty result`);
      }
    } catch (error) {
      console.log(`   ❌ Error in extractCleanSheetData:`, error.toString());
    }
    
  } catch (error) {
    console.log(`\n❌ Error testing ${betName}:`, error.toString());
  }
}

// Test the complete flow
function testCompleteCleanSheetFlow() {
  console.log('\n=== TESTING COMPLETE CLEAN SHEET FLOW ===');
  
  const fixtureId = '1338466';
  
  try {
    console.log('Calling getOddsForWeb...');
    const result = getOddsForWeb(fixtureId);
    
    console.log('\ngetOddsForWeb result:');
    console.log(JSON.stringify(result, null, 2));
    
    console.log('\nClean Sheet Analysis:');
    console.log('- cleanSheetHome exists:', !!result.cleanSheetHome);
    console.log('- cleanSheetHome length:', result.cleanSheetHome?.length || 0);
    console.log('- cleanSheetAway exists:', !!result.cleanSheetAway);
    console.log('- cleanSheetAway length:', result.cleanSheetAway?.length || 0);
    
    if (result.cleanSheetHome && result.cleanSheetHome.length > 0) {
      console.log('- cleanSheetHome data:', JSON.stringify(result.cleanSheetHome, null, 2));
    }
    
    if (result.cleanSheetAway && result.cleanSheetAway.length > 0) {
      console.log('- cleanSheetAway data:', JSON.stringify(result.cleanSheetAway, null, 2));
    }
    
  } catch (error) {
    console.log('Error in testCompleteCleanSheetFlow:', error.toString());
  }
}

// Simple test to see if the issue is in the extraction function
function testExtractionFunction() {
  console.log('\n=== TESTING EXTRACTION FUNCTION WITH SAMPLE DATA ===');
  
  // Create sample clean sheet data structure
  const sampleCleanSheetData = {
    fixture: { id: 1338466 },
    league: { name: "Test League" },
    bookmakers: [
      {
        id: 1,
        name: "Test Bookmaker",
        bets: [
          {
            id: 27,
            name: "Clean Sheet - Home",
            values: [
              { value: "Yes", odd: "2.50" },
              { value: "No", odd: "1.50" }
            ]
          }
        ]
      }
    ]
  };
  
  console.log('Sample data:', JSON.stringify(sampleCleanSheetData, null, 2));
  
  try {
    const processed = extractCleanSheetData(sampleCleanSheetData);
    console.log('Processed result:', JSON.stringify(processed, null, 2));
    
    if (processed && processed.length > 0) {
      console.log('✅ Extraction function works with sample data');
    } else {
      console.log('❌ Extraction function failed with sample data');
    }
  } catch (error) {
    console.log('❌ Error in extraction function:', error.toString());
  }
}