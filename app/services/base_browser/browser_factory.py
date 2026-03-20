from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

class BrowserFactory:
    def __init__(self, downloads_dir: str = '', headless: bool = True, path_name: str = ''):
        
        name_path = os.path.join("downloads", path_name)
        
        self.downloads_dir = downloads_dir or os.path.abspath(name_path)
        
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)
        
        self.headless = headless
        self.driver = self._create_driver()

    def _create_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless")

        prefs = {
            "download.default_directory": self.downloads_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }

        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")
        options.add_argument("--force-device-scale-factor=0.5")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        return driver

    def get_driver(self):
        return self.driver

    def quit(self):
        if self.driver:
            self.driver.quit()
