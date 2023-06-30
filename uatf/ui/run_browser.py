from selenium import webdriver

class RunBrowser:

    def run_chrome(self):
        """Запускаем хром"""

        return webdriver.Chrome()