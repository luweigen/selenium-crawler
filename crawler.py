from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datafile import DataFileHandler

import random
import time

class Action:
    def __init__(self):
        pass

    def execute(self, driver):
        raise NotImplementedError("Execute method should be implemented by subclasses")

class RecordItems(Action):
    def __init__(self, url, query, items_sel, item_selectors, main_key, next_pg_sel, open_details, details_selectors, close_details):
        super().__init__()
        self.items_sel = items_sel
        self.item_selectors = item_selectors
        self.main_key = main_key
        self.next_pg_sel = next_pg_sel
        self.open_details = open_details
        self.details_selectors = details_selectors
        self.close_details = close_details
        self.url = url
        self.query = query
        site = self.extract_site_name(url)
        self.data_handler = DataFileHandler(main_key=main_key, site=site, query=query)

    def extract_site_name(self, url):
        return url.split("//")[1].split("/")[0].split(".")[-2]

    def execute(self, driver):
        counter = 0
        load_next_page = True
        last_pg_txt = ''

        while load_next_page:
            try:
                found = False
                for _ in range(6):
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.items_sel)))
                    items = driver.find_elements(By.CSS_SELECTOR, self.items_sel)
                    if items and items[-1].text != last_pg_txt:
                        last_pg_txt = items[-1].text
                        found = True
                        break
                    else:
                        print("retry next page")
                        self.go_next_page()

                        time.sleep(5)

                if not found:
                    break
            except Exception as e:
                break

            for i, el in enumerate(items):
                data = self.extract_item_data(el, driver)

                # Check for duplicates
                if self.data_handler.is_duplicate(data.get(self.main_key, '')):
                    print("Duplicate found, stopping.")
                    load_next_page = False
                    break

                if not data.get(self.main_key, ''):
                    break

                print(data)        
                self.data_handler.append_data(data)

            if load_next_page:
                load_next_page = self.go_next_page(driver)

                time.sleep(random.randrange(1, 5))
                counter += 1
                print('Page:', counter)

    def go_next_page(self, driver):
        try:
            nextButton = driver.find_elements(By.CSS_SELECTOR, self.next_pg_sel)
            if not nextButton:
                return False
            driver.click_element(nextButton[0])
            return True
        except Exception as e:
            print("Error moving to next page:", e)
            return False

    def extract_item_data(self, el, driver):
        data = {}

        for key, sel in self.item_selectors.items():
            data[key] = driver.extract_data(el, sel)#from el

        # Handle details if necessary
        if self.open_details:
            try:
                if 'selector' in self.open_details:
                    elem = el.find_element(By.CSS_SELECTOR, self.open_details['selector'])
                    self.driver.click_element(elem)
                time.sleep(2)
                for k, s in self.details_selectors.items():
                    data[k] = driver.extract_data(driver, s)#from entire document

                if self.close_details:
                    if 'selector' in self.close_details:
                        close = self.driver.find_element(By.CSS_SELECTOR, self.close_details['selector'])
                        self.driver.click_element(close)
            except Exception as e:
                for k, s in self.details_selectors.items():
                    data[k] = ""

        return data

class Crawler:
    def __init__(self, driver, url, query, actions):
        self.driver = driver
        self.url = url
        self.actions = actions
        self.query = query

    def run(self):
        self.driver.get(self.url)
        time.sleep(2)

        for action in self.actions:
            action.execute(self.driver)