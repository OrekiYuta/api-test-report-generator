import sys
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from utils.PathManager import load_path_manager as lpm


class ChromeDriverManager:
    def __init__(self):
        self.driver = None

    @staticmethod
    def install_chromedriver():
        chromedriver_autoinstaller.install(path=str(lpm.chromedriver))

    @staticmethod
    def configure_chrome_options():
        chrome_options = Options()
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument("--headless=new")
        return chrome_options

    def create_driver(self):
        self.install_chromedriver()
        chrome_options = self.configure_chrome_options()

        if sys.platform.startswith("win"):
            chrome_driver_file_name = "chromedriver.exe"
        else:
            chrome_driver_file_name = "chromedriver"

        chrome_driver_path = lpm.chromedriver(
            chromedriver_autoinstaller.get_chrome_version().split(".")[0] + "\\" + chrome_driver_file_name)
        chrome_service = ChromeService(chrome_driver_path)
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        self.driver.implicitly_wait(20)

    def get_driver(self):
        if self.driver is None:
            self.create_driver()
        return self.driver

    def close_driver(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None


if __name__ == '__main__':

    driver_manager = ChromeDriverManager()

    try:
        driver = driver_manager.get_driver()
        driver.get('https://google.com')
    finally:
        driver_manager.close_driver()
