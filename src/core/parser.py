import time
import random
from .article import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException


class Parser:
    def __init__(self, requested_link):
        self.driver = self.create_stealth_headless_driver()
        self.driver.get(requested_link)
        
        wait = WebDriverWait(self.driver, timeout=90)
        wait.until(lambda d: 'Ray ID' not in d.page_source)

        self.driver.find_element(By.ID, 'didomi-notice-agree-button').click()
        self.human_like_delay()

        print('PARSER INITIALIZED')
    
    def parse(self):
        articles_container = self.driver.find_element(By.CLASS_NAME, 'js-items')
        arctiles = articles_container.find_elements(By.CLASS_NAME, 'nova-legacy-o-stack__item')
        self.human_like_delay()
        for article in arctiles:
            link = article.find_element(By.TAG_NAME, 'a')
            self.scroll(link)
            self.move_mouse(link)
            link.click()
            self.human_like_delay()
            self.driver.find_element(By.CLASS_NAME, 'gtm-download-fulltext-btn-header-promo').click()

    def human_like_delay(self, min_seconds=2, max_seconds=8):
        """Randomized delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        
        # Add micro-delays within the wait
        steps = random.randint(3, 8)
        step_delay = delay / steps
        
        for i in range(steps):
            time.sleep(step_delay)
            # Simulate occasional mouse movement
            if random.random() > 0.7:
                self.driver.execute_script(f"""
                    window.dispatchEvent(new MouseEvent('mousemove', {{
                        clientX: {random.randint(0, 1000)},
                        clientY: {random.randint(0, 800)}
                    }}));
                """)
    
    
    def scroll(self, element):
        ActionChains(self.driver).scroll_to_element(element).perform()
    
    def move_mouse(self, element):
        self.driver.execute_script(f"""
            window.dispatchEvent(new MouseEvent('mousemove', {{
                clientX: {element.location['x']},
                clientY: {element.location['y']}
            }}));
        """)
    
    def next_page(self):
        pagination = self.driver.find_element(By.CLASS_NAME, 'pager-container')
        next_page_button = pagination.find_elements(By.CLASS_NAME, 'nova-legacy-c-button-group__item')[-1]
        try:
            next_page_button.find_element(By.TAG_NAME, 'button')
            return 'END'
        except NoSuchElementException:
            pass
        ActionChains(self.driver).scroll_to_element(next_page_button).perform()
        next_page_button.find_element(By.TAG_NAME, 'a').click()
        self.driver.execute_script(f"""
                    window.dispatchEvent(new MouseEvent('mousemove', {{
                        clientX: {random.randint(0, 1000)},
                        clientY: {random.randint(0, 800)}
                    }}));
                """)
    
    @staticmethod
    def get_link(div):
        return div.find_element(By.CLASS_NAME, 'nova-legacy-e-link')

    @staticmethod
    def get_date(div):
        e_list = div.find_element(By.TAG_NAME, 'ul')
        date_text = e_list.find_element(By.TAG_NAME, 'li')
        print(date_text.text)

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
