from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class BrowserDriver:
    def __init__(self):
        self.driver = None

    def click_element(self, el):
        """
        This method needs to be implemented by each subclass.
        """
        raise NotImplementedError

    def quit(self):
        if self.driver:
            self.driver.quit()

    def __getattr__(self, item):
        """
        Delegate attribute access to the WebDriver instance.
        """
        return getattr(self.driver, item)

class ChromeDriver(BrowserDriver):
    def __init__(self, chrome_options, path):
        super().__init__()
        service = Service(executable_path=path)
        self.driver = webdriver.Chrome(options=chrome_options, service=service)

    def click_element(self, elem):
        elem.click()


class SafariDriver(BrowserDriver):
    def __init__(self):
        super().__init__()
        self.driver = webdriver.Safari()

    def click_element(self, elem):
        self.driver.execute_script("arguments[0].click();", elem)


# Example usage
#path_to_chromedriver = '/path/to/chromedriver'  # Replace with the actual path
#chrome = ChromeDriver(path_to_chromedriver)
#safari = SafariDriver()

# Perform actions
# For example, assuming 'el'
# chrome.click_element(el)
# safari.click_element(el)

# Quit drivers
# chrome.quit()
# safari.quit()
