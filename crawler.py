from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datafile import DataSQLiteHandler, DataFileHandler, print_err

import random
import time

class Action:
    def __init__(self):
        pass

    def execute(self, driver, do_on_success=None):
        raise NotImplementedError("Execute method should be implemented by subclasses")


class Input(Action):
    def __init__(self, inputs, confirm_sel, wait=2):
        super().__init__()
        self.inputs = inputs
        self.confirm_sel = confirm_sel
        self.wait = wait

    def execute(self, driver, do_on_success=None):
        try:
            # wait content to be loaded
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.confirm_sel)))

            if do_on_success:
                do_on_success()
            
            for inp in self.inputs:
                queryInput = driver.find_element(By.CSS_SELECTOR, inp['selector'])
                queryInput.click()
                queryInput.clear()
                queryInput.send_keys(inp['value'])
            
            queryButtons = driver.find_elements(By.CSS_SELECTOR, self.confirm_sel)

            if queryButtons:
                queryButtons[0].click()
                if self.wait<0:
                    print_err("Enter to continue:",end="")
                    input()
                else:
                    time.sleep(self.wait)
        except Exception as e:
            print_err(f"Input.execute error {e}")


class RecordItems(Action):
    def __init__(self, url, query, items_sel, item_selectors, main_key, second_key=None, time_key=None, consecutive_duplicate=1, next_pg_sel=None, next_pg_act=None, open_details=None, details_selectors=None, close_details=None, storage=None):
        super().__init__()
        self.items_sel = items_sel
        self.item_selectors = item_selectors
        self.main_key = main_key
        self.second_key = second_key
        #self.time_key = time_key
        self.consecutive_duplicate = consecutive_duplicate
        self.next_pg_sel = next_pg_sel
        self.next_pg_act = next_pg_act
        self.open_details = open_details
        self.details_selectors = details_selectors
        self.close_details = close_details
        self.url = url
        self.query = query
        site = self.extract_site_name(url)
        if storage=="sql":
            self.data_handler = DataSQLiteHandler(main_key=main_key, site=site, query=query, second_key=second_key, time_key=time_key)
        else:
            self.data_handler = DataFileHandler(main_key=main_key, site=site, query=query)

    def extract_site_name(self, url):
        return url.split("//")[1].split("/")[0].split(".")[-2]

    def execute(self, driver, do_on_success=None):
        counter = 0
        load_next_page = True
        #last_pg_txt = ''
        recent_duplicates = []

        while load_next_page:
            try:
                found = False
                for _ in range(6):
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.items_sel)))
                    items = driver.find_elements(By.CSS_SELECTOR, self.items_sel)
                    if items and not driver.is_element_visited(items[-1]):#items[-1].text != last_pg_txt:
                        #last_pg_txt = items[-1].text
                        found = True
                        #有新数据了，但在前面的就数据可能没从DOM里删除
                        break
                    else:
                        print_err("retry next page")
                        self.go_next_page(driver)

                        time.sleep(5)

                if do_on_success:
                    do_on_success()

                if not found:
                    break
            except Exception as e:
                break

            for i, el in enumerate(items):
                if driver.is_element_visited(el):
                    #print_err(f"Skip {el.get_attribute('outerHTML')}")
                    continue

                data = self.extract_item_data(el, driver)

                # Check for duplicates
                current_key = (data.get(self.main_key, ''), data.get(self.second_key, None) if self.second_key else None)

                if self.data_handler.is_duplicate(*current_key):
                    recent_duplicates.append(data)
                    if len(recent_duplicates) >= self.consecutive_duplicate:
                        print_err(f"Duplicate found, stopping. Recent duplicates:\n{recent_duplicates}")
                        load_next_page = False
                        break
                else:
                    recent_duplicates.clear()  # 清空队列，因为找到了一个新的非重复项

                if not data.get(self.main_key, ''):
                    break

                print(data)        
                self.data_handler.append_data(data)

            if load_next_page:
                load_next_page = self.go_next_page(driver)

                time.sleep(random.randrange(1, 5))
                counter += 1
                print_err(f'Page:{counter}')

        self.data_handler.save_main_file()

    def go_next_page(self, driver):
        try:
            if self.next_pg_sel:
                nextButton = driver.find_elements(By.CSS_SELECTOR, self.next_pg_sel)
                if not nextButton:
                    return False
                driver.click_element(nextButton[0])
            if self.next_pg_act=="scroll":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            return True
        except Exception as e:
            print_err(f"Error moving to next page:{e}")
            return False

    def extract_item_data(self, el, driver):
        data = {}

        for key, sel in self.item_selectors.items():
            #print_err(f"{key}-{sel}")
            data[key] = driver.extract_data(el, sel)#from el
            #print_err(data[key])

        # Handle details if necessary
        if self.open_details:
            try:
                if 'selector' in self.open_details:
                    elem = el.find_element(By.CSS_SELECTOR, self.open_details['selector'])
                    driver.click_element(elem)
                time.sleep(2)
                for k, s in self.details_selectors.items():
                    data[k] = driver.extract_data(driver, s)#from entire document

                if self.close_details:
                    if 'selector' in self.close_details:
                        close = driver.find_element(By.CSS_SELECTOR, self.close_details['selector'])
                        driver.click_element(close)
            except Exception as e:
                #print_err(f"open details error:{e}")
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
        self.driver.load_url_with_ookies(self.url)
        time.sleep(2)

        for action in self.actions:
            action.execute(self.driver, do_on_success=lambda : self.driver.save_cookies_for_url(self.url))