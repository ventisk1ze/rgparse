from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class Parser:
    def __init__(self, requested_link):
        self.driver = self.create_stealth_headless_driver()
        self.driver.get(requested_link)
        
        wait = WebDriverWait(self.driver, timeout=60)
        wait.until(lambda d: 'Ray ID' not in d.page_source)

        
    def parse(self):
        articles_container = self.driver.find_element(By.CLASS_NAME, 'js-items')
        divs = articles_container.find_elements(By.CLASS_NAME, 'nova-legacy-o-stack__item')
    
    @staticmethod
    def get_link(self, div):
        pass

    @staticmethod
    def get_date(self, div):
        pass

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
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
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
