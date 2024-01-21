from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from compatibledriver import ChromeDriver, SafariDriver
from datafile import DataFileHandler

import random
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--keyword', type=str, default='AI', help="keyword")
args = parser.parse_args()



chrome_options = Options()
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1200x880")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--user-data-dir=C:/Users/Acer/AppData/Local/Google/Chrome/User Data')
# chrome_options.add_argument('--profile-directory=Profile 1'),
# chrome_options.add_argument('--headless')

driver = SafariDriver()#ChromeDriver(chrome_options, './chromedriver-mac-arm64/chromedriver')


if len(args.keyword)<1:
    print('Enter keyword: ',end='')
    keyword = input()
else:
    keyword = args.keyword

data_handler = DataFileHandler(main_key='job_link', site='upwork', query=keyword)

url = f'https://www.upwork.com/nx/search/jobs/?nbs=1&page=1&q={keyword}&sort=recency'
#TODO: LLM to find these
items_sel = "section[data-test='JobsList'] > article"
item_selectors = {
    "posted_time": "div.job-tile-header small span:nth-of-type(2)",
    "job_title": "h2.job-tile-title a",
    "job_type": "li[data-test='job-type-label']",
    "experience_level": "li[data-test='experience-level']",
    "duration_hours": "li[data-test='duration-label']",
    "job_description": "div[data-test='JobDescription'] p",
    "skill_tags": {
        "selector": "span[data-test='token'] span",
        "type": "multi-text"
    },
    "job_link": {
        "selector": "h2.job-tile-title a[href]",
        "type": "attr"
    }
}
next_pg_sel = "button[data-ev-label='pagination_next_page']"
detail_open_sel = "h2.job-tile-title a"
details_selectors = {
    "location":'div.job-details-loader div[data-test="LocationLabel"]',
    "client_location": "div.job-details-loader li[data-qa='client-location']",
    "client_job_posting_stats": "div.job-details-loader li[data-qa='client-job-posting-stats']",
    "client_activity": 'div.job-details-loader ul.client-activity-items',
    "client_contract_date": 'div.job-details-loader div[data-qa="client-contract-date"]'
}
detail_close_sel = "button[data-test='slider-close-desktop']"

driver.get(url)
time.sleep(2)

counter = 0

last_pg_txt = ''

def go_next_page(driver, next_pg_sel):
    # detect next button
    nextButton = driver.find_elements(By.CSS_SELECTOR, next_pg_sel)

        
    # detect next button disabled
    if (len(nextButton) == 0):
        raise Exception('Not found',next_pg_sel)
    
    # move to next page
    #nextButton[0].click()
    #driver.execute_script("arguments[0].click();", nextButton[0])#walk around for Safari
    driver.click_element(nextButton[0])

load_next_page = True
while load_next_page:

    try:
        found = False
        for i in range(6):
            # wait content to be loaded
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, items_sel)))
            items = driver.find_elements(By.CSS_SELECTOR, items_sel)
            if len(items)>0 and items[-1].text!=last_pg_txt:
                last_pg_txt = items[-1].text
                print(f"{items_sel} found")
                found = True
                break
            else:
                print("retry next page")
                go_next_page(driver,next_pg_sel)

                time.sleep(5)

        if not found:
            break
    except:
        break

    for i in range(len(items)):
        el = items[i]
        #print(f"{i} ### {el.get_attribute('innerHTML')}")   #TODO: LLM to parse HTML
        data = {}

        for key, sel in item_selectors.items():
            data[key] = driver.extract_data(el, sel)

        if detail_open_sel:
            try:
                elem = el.find_element(By.CSS_SELECTOR, detail_open_sel)
                driver.click_element(elem)
                time.sleep(2)
                for k, s in details_selectors.items():
                    data[k] = driver.extract_data(driver, s)
                close = driver.find_element(By.CSS_SELECTOR, detail_close_sel)
                driver.click_element(close)
            except:
                for k, s in details_selectors.items():
                    data[k] = ""

        # 检查是否有重复的job_link
        current_job_link = data.get('job_link', '')
        if data_handler.is_duplicate(current_job_link):
            load_next_page = False
            break  # 如果发现重复的job_link，结束循环

        print(data)        

        data_handler.append_data(data)

    if load_next_page:
        try:
            go_next_page(driver,next_pg_sel)
        except:
            break
        time.sleep(random.randrange(1, 5))

        counter += 1
        print('page: ' + str(counter))

data_handler.save_main_file()
driver.quit()
            