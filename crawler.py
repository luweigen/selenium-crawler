from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datafile import DataFileHandler

import random
import time

class Crawler:
    def __init__(self, driver, site_model, query):
        self.driver = driver
        self.site_model = site_model
        self.query = query

        # 提取网站名称作为site参数
        site = self.extract_site_name(site_model['url'])
        self.data_handler = DataFileHandler(main_key=site_model['main_key'], site=site, query=self.query)

    def extract_site_name(self, url):
        # 实现从URL中提取网站名称的逻辑
        # 例如：从 "https://www.upwork.com/nx/search/jobs/..." 中提取 "upwork"
        # 这里的实现可能需要根据实际URL格式进行调整
        return url.split("//")[1].split("/")[0].split(".")[-2]

    def run(self):
        url = self.site_model['url']
        self.driver.get(url)
        time.sleep(2)

        counter = 0
        load_next_page = True
        last_pg_txt = ''

        while load_next_page:
            try:
                found = False
                for _ in range(6):
                    WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.site_model['items_sel'])))
                    items = self.driver.find_elements(By.CSS_SELECTOR, self.site_model['items_sel'])
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
                data = self.extract_item_data(el)

                # 检查是否有重复的数据
                if self.data_handler.is_duplicate(data.get(self.site_model['main_key'], '')):
                    print("Over w/ is_duplicate")
                    load_next_page = False
                    break

                if not data.get(self.site_model['main_key'], ''):
                    break;

                print(data)        

                self.data_handler.append_data(data)

            if load_next_page:
                try:
                    self.go_next_page()
                except Exception as e:
                    break
                time.sleep(random.randrange(1, 5))

                counter += 1
                print('page:', counter)

        self.data_handler.save_main_file()

    def go_next_page(self):
        nextButton = self.driver.find_elements(By.CSS_SELECTOR, self.site_model['next_pg_sel'])
        if not nextButton:
            raise Exception('Not found', self.site_model['next_pg_sel'])
        self.driver.click_element(nextButton[0])

    def extract_item_data(self, el):
        data = {}

        for key, sel in self.site_model['item_selectors'].items():
            data[key] = self.driver.extract_data(el, sel)

        if self.site_model['detail_open_sel']:
            try:
                elem = el.find_element(By.CSS_SELECTOR, self.site_model['detail_open_sel'])
                self.driver.click_element(elem)
                time.sleep(2)
                for k, s in self.site_model['details_selectors'].items():
                    data[k] = self.driver.extract_data(self.driver, s)

                if self.site_model['detail_close_sel']:
                    close = self.driver.find_element(By.CSS_SELECTOR, self.site_model['detail_close_sel'])
                    self.driver.click_element(close)
            except Exception as e:
                for k, s in self.site_model['details_selectors'].items():
                    data[k] = ""
        return data

