#!/usr/bin/env python3
"""
Basic Test Script for Parimatch Access
This tests if we can access Parimatch and see basic page content
"""

def test_basic_access():
    """Test basic access to Parimatch"""
    print("🧪 Testing basic Parimatch access...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        import time
        
        # Setup Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Try to create driver
        try:
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
        except:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Chrome driver created successfully")
        
        # Test basic page access
        test_url = "https://parimatchglobal.com"
        print(f"🌐 Accessing: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check page content
        page_source = driver.page_source.lower()
        print(f"📏 Page size: {len(page_source)} characters")
        
        # Look for key indicators
        indicators = ['parimatch', 'football', 'sport', 'premier', 'league']
        found_indicators = [ind for ind in indicators if ind in page_source]
        
        if found_indicators:
            print(f"✅ Found indicators: {found_indicators}")
            print("✅ Basic access is working!")
        else:
            print("⚠️ Page loaded but no key indicators found")
            print("This might mean:")
            print("  - Page is blocked or showing captcha")
            print("  - Different page structure")
            print("  - Site is down")
        
        # Check for blocking signs
        blocking_signs = ['blocked', 'captcha', 'robot', 'access denied']
        found_blocks = [sign for sign in blocking_signs if sign in page_source]
        
        if found_blocks:
            print(f"❌ Blocking detected: {found_blocks}")
        else:
            print("✅ No obvious blocking detected")
        
        # Test Premier League URL
        pl_url = "https://parimatchglobal.com/en/football/premier-league-7f5506e872d14928adf0613efa509494/prematch"
        print(f"\n🏆 Testing Premier League page: {pl_url}")
        
        driver.get(pl_url)
        time.sleep(5)
        
        print(f"📄 PL page title: {driver.title}")
        
        pl_page = driver.page_source.lower()
        pl_teams = ['liverpool', 'arsenal', 'chelsea', 'manchester', 'tottenham']
        found_teams = [team for team in pl_teams if team in pl_page]
        
        if found_teams:
            print(f"⚽ Premier League teams found: {found_teams}")
            print("✅ Premier League page accessible!")
        else:
            print("❌ No Premier League teams found")
            print("This could mean:")
            print("  - No matches available today")
            print("  - Different URL structure")
            print("  - Page not loading correctly")
        
        # Check for links
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"🔗 Total links found: {len(links)}")
        
        # Look for event/match links
        event_links = []
        for link in links[:50]:  # Check first 50 links
            try:
                href = link.get_attribute('href')
                if href and ('/events/' in href or '/match' in href.lower()):
                    event_links.append(href)
            except:
                continue
        
        if event_links:
            print(f"🎯 Found {len(event_links)} potential event links")
            print(f"Sample: {event_links[0][:80]}...")
            print("✅ Match links are available!")
        else:
            print("❌ No event/match links found")
        
        driver.quit()
        print("\n🎉 Basic test completed!")
        
        # Summary
        print("\n📊 SUMMARY:")
        if found_indicators and not found_blocks:
            print("✅ Parimatch access is working")
        else:
            print("⚠️ Parimatch access has issues")
            
        if found_teams:
            print("✅ Premier League page is accessible")
        else:
            print("❌ Premier League page has issues")
            
        if event_links:
            print("✅ Match links are available")
        else:
            print("❌ No match links found")
            
        return len(found_indicators) > 0 and len(found_blocks) == 0
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    import subprocess
    import sys
    
    packages = ['selenium', 'webdriver-manager']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")
        except:
            print(f"❌ Failed to install {package}")

if __name__ == "__main__":
    print("🧪 PARIMATCH BASIC ACCESS TEST")
    print("=" * 40)
    
    # Install requirements if in Colab
    try:
        import google.colab
        print("🔧 Google Colab detected - installing packages...")
        install_requirements()
        
        # Install Chrome in Colab
        import subprocess
        subprocess.run(['apt-get', 'update'], capture_output=True)
        subprocess.run(['apt-get', 'install', '-y', 'chromium-browser', 'chromium-chromedriver'], capture_output=True)
        print("✅ Chrome installed for Colab")
        
    except ImportError:
        print("💻 Local environment detected")
    
    # Run the test
    success = test_basic_access()
    
    if success:
        print("\n🎉 Test PASSED - Parimatch scraper should work!")
    else:
        print("\n❌ Test FAILED - Issues detected with Parimatch access")
        print("Try running the full scraper to see detailed debug info")