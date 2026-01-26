import re
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

DATE_PATTERN = re.compile(
    r'\b(\d{1,2})\s+([Jj]anuary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Mm]ay|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember|[Oo]ctober|[Nn]ovember|[Dd]ecember)\s+(\d{4})\b'
)

class IEEEParser:
    def __init__(self, requested_link):
        self.driver = self.create_stealth_headless_driver()
        self.driver.get(requested_link)

        print('PARSER INITIALIZED')

    def parse(self):
        wait = WebDriverWait(self.driver, timeout=60)
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'List-results-items'))
        )
        search_results = self.driver.find_elements(By.CLASS_NAME, 'List-results-items')
        suitable_results = (sr for sr in search_results if self.is_suitable_search_result(sr))
        links = [sr.find_element(By.CLASS_NAME, 'fw-bold').get_attribute('href') for sr in suitable_results]
        for link in links:
            self.driver.get(link)
            try:
                date_string = ' '.join(DATE_PATTERN.findall(self.driver.page_source)[0])
                date = datetime.strptime(date_string, '%d %B %Y').date()
            except IndexError:
                print('Publication date not found')
            if date < datetime.strptime('01.10.2025', '%d.%m.%Y').date():
                continue

            pdf_button = self.driver.find_element(By.CLASS_NAME, 'xpl-btn-pdf')
            pdf_link = pdf_button.get_attribute('href')

            pdf_button.click()
            if 'denied' in self.driver.current_url:
                self.driver.get(pdf_link)

            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
            
            if 'denied' in self.driver.current_url:
                print('Access to article denied')
                return

            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
            frames = self.driver.find_elements(By.TAG_NAME, 'iframe')
            print(len(frames))
            for element in frames:
                print('IFRAME')
                self.driver.switch_to.frame(element)
                try:
                    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
                    print('found inner iframe')
                    self.driver.switch_to.frame(
                        self.driver.find_element(By.TAG_NAME, 'iframe')
                    )
                    wait.until(EC.presence_of_all_elements_located((By.ID, 'save')))
                except TimeoutException:
                    print('TIMEOUT')
                    self.driver.switch_to.default_content()
                    continue

                print(element.find_element(By.ID, 'save'))
                break
        
    
    @staticmethod
    def is_suitable_search_result(element):
        try:
            element.find_element(By.CLASS_NAME, 'icon-access-open-access')
        except NoSuchElementException:
            return False
        link = element.find_element(By.CLASS_NAME, 'fw-bold')
        return 'Process Mining' in link.text
    
    @staticmethod
    def create_stealth_headless_driver():
        options = Options()
        
        # Use new headless mode
        options.add_argument('--headless=new')
        
        # Disable automation flags
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Normal browser settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Realistic user agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
        
        # Enable features
        options.add_argument('--enable-webgl')
        options.add_argument('--enable-3d-apis')
        options.add_argument('--enable-javascript')

        options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Disable logging
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        # Set preferences
        prefs = {
            "download.default_directory": './downloads',
            "download.prompt_for_download": False,  # Disable download prompt
            "download.directory_upgrade": True,
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Create driver
        driver = webdriver.Chrome(options=options)
        
        # Execute stealth scripts
        stealth_scripts = [
            # Hide automation
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ? 
                    Promise.resolve({ state: Notification.permission }) : 
                    originalQuery(parameters)
            );
            """,
            
            # Spoof hardware concurrency
            """
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            """,
        ]
        
        for script in stealth_scripts:
            driver.execute_script(script)
        
        return driver