// Quick test to see what getOddsForWeb is actually returning
function testCurrentImplementation() {
  console.log('=== TESTING CURRENT IMPLEMENTATION ===');
  
  const fixtureId = '1338466';
  console.log('Testing fixture ID:', fixtureId);
  
  try {
    const result = getOddsForWeb(fixtureId);
    console.log('getOddsForWeb result:', JSON.stringify(result, null, 2));
    
    // Check specifically for clean sheet data
    console.log('\nClean Sheet Home Data:', result.cleanSheetHome);
    console.log('Clean Sheet Away Data:', result.cleanSheetAway);
    
    // Check if the data exists but is empty
    if (result.cleanSheetHome !== undefined) {
      console.log('Clean Sheet Home length:', result.cleanSheetHome.length);
    } else {
      console.log('Clean Sheet Home is undefined');
    }
    
    if (result.cleanSheetAway !== undefined) {
      console.log('Clean Sheet Away length:', result.cleanSheetAway.length);
    } else {
      console.log('Clean Sheet Away is undefined');
    }
    
    return result;
    
  } catch (error) {
    console.log('Error in testCurrentImplementation:', error.toString());
    return { error: error.toString() };
  }
}

// Test just the clean sheet fetching part
function testCleanSheetFetchOnly() {
  console.log('=== TESTING CLEAN SHEET FETCH ONLY ===');
  
  const fixtureId = '1338466';
  const API_KEY = 'aa0498aa71mshc3f6f0728d1cc2ap14aa0ajsnb7f01ea658a0';
  const BASE_URL_ODDS = 'https://api-football-v1.p.rapidapi.com/v3/odds';
  
  try {
    // Test Home Clean Sheet
    console.log('Fetching Home Clean Sheet...');
    const homeData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, '27');
    console.log('Home Clean Sheet Raw Data:', JSON.stringify(homeData, null, 2));
    
    if (homeData && homeData.bookmakers) {
      const homeProcessed = extractCleanSheetData(homeData);
      console.log('Home Clean Sheet Processed:', JSON.stringify(homeProcessed, null, 2));
    } else {
      console.log('No home clean sheet data available');
    }
    
    // Test Away Clean Sheet
    console.log('\nFetching Away Clean Sheet...');
    const awayData = fetchOddsData(BASE_URL_ODDS, API_KEY, fixtureId, '28');
    console.log('Away Clean Sheet Raw Data:', JSON.stringify(awayData, null, 2));
    
    if (awayData && awayData.bookmakers) {
      const awayProcessed = extractCleanSheetData(awayData);
      console.log('Away Clean Sheet Processed:', JSON.stringify(awayProcessed, null, 2));
    } else {
      console.log('No away clean sheet data available');
    }
    
  } catch (error) {
    console.log('Error in testCleanSheetFetchOnly:', error.toString());
  }
}