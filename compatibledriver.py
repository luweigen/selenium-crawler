from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
import json
import os
import platform

class BrowserDriver:
    def __init__(self):
        self.driver = None

    def click_element(self, el):
        """
        This method needs to be implemented by each subclass.
        """
        raise NotImplementedError

    def ctrl_click(self, el):
        ctrl = Keys.CONTROL
        if platform.system()=='Darwin':
            ctrl = Keys.COMMAND
        ActionChains(self.driver)\
        .key_down(ctrl)\
        .click(el)\
        .key_up(ctrl)\
        .perform()

    def quit(self):
        if self.driver:
            self.driver.quit()

    def save_cookies_to_path(self,path):
        # Get and store cookies after login
        cookies = self.driver.get_cookies()

        # Store cookies in a file
        with open(path, 'w') as file:
            json.dump(cookies, file)
        print(f'New Cookies saved to {path} successfully')


    def load_cookies_from_path_to_url(self, path, url):
        self.driver.get(url)
        # Check if cookies file exists
        if path in os.listdir():

            # Load cookies to a vaiable from a file
            with open(path, 'r') as file:
                cookies = json.load(file)

            # Set stored cookies to maintain the session
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            self.driver.get(url)
        else:
            print(f'No cookies {path} file found')
    
        #driver.refresh() # Refresh Browser after login

    def extract_data(self, element, selector_info):
        try:
            if isinstance(selector_info, str):  # Simple selector
                return element.find_element(By.CSS_SELECTOR, selector_info).text.strip()
            else:  # Dictionary with additional instructions
                elements = element.find_elements(By.CSS_SELECTOR, selector_info["selector"])
                if selector_info["type"] == "multi-text":
                    return [elem.text.strip() for elem in elements]
                elif selector_info["type"] == "multi-html":
                    return [elem.get_attribute('innerHTML').strip() for elem in elements]
                elif selector_info["type"] == "attr":
                    sel = selector_info["selector"]
                    attr_name = sel[sel.rfind('[')+1 : sel.rfind(']')]
                    return elements[0].get_attribute(attr_name) if elements else ""
                elif selector_info["type"] == "multi-attr":
                    sel = selector_info["selector"]
                    attr_name = sel[sel.rfind('[')+1 : sel.rfind(']')]
                    return [elem.get_attribute(attr_name).strip() for elem in elements]
                elif selector_info["type"] == "html":
                    return elements[0].get_attribute('innerHTML').strip()
        except:
            print(f"{selector_info} not found")
            if isinstance(selector_info, dict) and "type" in selector_info and selector_info["type"].startswith("multi"):
                return []  # Return empty list for multi-valued selectors
            else:
                return ""  # Return empty string for single-valued selectors        

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
