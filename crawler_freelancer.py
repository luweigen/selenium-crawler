from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
import random
import time
from datetime import datetime
from email.utils import formatdate
import re
import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--keyword', type=str, default='AI', help="keyword")
args = parser.parse_args()

import signal

def handler(signum, frame):
    save_main_file()

signal.signal(signal.SIGINT, handler)


service = Service(executable_path='./chromedriver-mac-arm64/chromedriver')

chrome_options = Options()
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1200x880")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--user-data-dir=C:/Users/Acer/AppData/Local/Google/Chrome/User Data')
# chrome_options.add_argument('--profile-directory=Profile 1'),
# chrome_options.add_argument('--headless')

if len(args.keyword)<1:
    print('Enter keyword: ',end='')
    keyword = input()
else:
    keyword = args.keyword

main_csv_file = f'freelancer-{keyword}.csv'
run_start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
temp_csv_file = f'freelancer-{run_start_time}.csv'
def save_main_file():
    if os.path.exists(temp_csv_file):
        temp_df = pd.read_csv(temp_csv_file)
        if not temp_df.empty:
            # 逆序DataFrame
            reversed_df = temp_df.iloc[::-1]
            if os.path.exists(main_csv_file):
                reversed_df.to_csv(main_csv_file, mode='a', index=False, header=False)
            else:
                reversed_df.to_csv(main_csv_file, mode='w', index=False, header=True)

        # 删除临时文件
        os.remove(temp_csv_file)

url = f'https://www.freelancer.com/jobs/?status=all'
site_model = {
    "url":f'https://www.upwork.com/nx/search/jobs/?nbs=1&page=1&q={keyword}&sort=recency',
    "pre-actions":[
        {
            "action":"input",
            "inputs":[
                {
                    "selector":"input#keyword-input",
                    "value":keyword
                }
            ],
            "confirm":"button#search-submit"
        }
    ],
    #items_sel to detail_close_sel 
}

driver = webdriver.Chrome(options=chrome_options, service=service)

driver.get(url)
time.sleep(2)

counter = 0
last_saved_job_link =''

#open document and start writing process
# 检查文件是否存在并读取最后一行
if os.path.exists(main_csv_file):
    df = pd.read_csv(main_csv_file)
    if not df.empty:
        last_saved_job_link = df.iloc[-1]['job_link']

load_next_page = True
while load_next_page:

    #TODO: LLM to find these
    query_btn_sel = "button#search-submit"
    query_input_sel = "input#keyword-input"
    items_sel = "div.JobSearchCard-item"
    item_selectors = {
        "posted_time": "span.JobSearchCard-primary-heading-days",
        "job_title": "div.JobSearchCard-primary-heading a",
        "job_type": "div.JobSearchCard-secondary-price",
        #"experience_level": "li[data-test='experience-level']",
        #"duration_hours": "li[data-test='duration-label']",
        "prop": "div.JobSearchCard-secondary-entry",
        "job_description": "p.JobSearchCard-primary-description"
    }
    item_multi_selectors = {
        "skill_tags": "div.JobSearchCard-primary-tags a"
    }
    item_attr_selectors = {
        "job_link": "div.JobSearchCard-primary-heading a[href]"
    }
    next_pg_sel = "li[data-link='next_page'] a"

    try:
        # wait content to be loaded
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, query_btn_sel)))
        
        queryInput = driver.find_element(By.CSS_SELECTOR, query_input_sel)
        queryInput.click()
        queryInput.clear()
        queryInput.send_keys(keyword)
        queryButtons = driver.find_elements(By.CSS_SELECTOR, query_btn_sel)

        if (len(queryButtons) == 0):
            break              
        queryButtons[0].click()
        time.sleep(2)

        # wait content to be loaded
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, items_sel)))
    except:
        break

    print(f"{items_sel} found")

    items = driver.find_elements(By.CSS_SELECTOR, items_sel)
    for i in range(len(items)):
        el = items[i]
        #print(f"{i} ### {el.get_attribute('innerHTML')}")   #TODO: LLM to parse HTML
        data = {}
        data['record_time'] = formatdate(localtime=True, usegmt=True)


        # 处理单个值的selectors
        for key, sel in item_selectors.items():
            try:
                data[key] = el.find_element(By.CSS_SELECTOR, sel).text
            except:
                data[key] = ""

        # 处理可能有多个值的multi_selectors
        for key, sel in item_multi_selectors.items():
            try:
                elements = el.find_elements(By.CSS_SELECTOR, sel)
                data[key] = [element.text for element in elements if element.text.strip()]
            except:
                data[key] = []

        # 处理属性的attr_selectors
        for key, sel in item_attr_selectors.items():
            try:
                attr_name = sel[sel.rfind('[')+1 : sel.rfind(']')]
                data[key] = el.find_element(By.CSS_SELECTOR, sel).get_attribute(attr_name)
            except:
                data[key] = ""

        # 检查是否有重复的job_link
        current_job_link = data.get('job_link', '')
        if current_job_link == last_saved_job_link:
            load_next_page = False
            break  # 如果发现重复的job_link，结束循环

        print(data)        

        # 将数据保存到CSV文件
        df = pd.DataFrame([data])
        if not os.path.exists(temp_csv_file):
            df.to_csv(temp_csv_file, mode='w', index=False, header=True)
        else:
            df.to_csv(temp_csv_file, mode='a', index=False, header=False)

    if load_next_page:
        # detect next button
        nextButton = driver.find_elements(By.CSS_SELECTOR, next_pg_sel)

            
        # detect next button disabled
        if (len(nextButton) == 0):
            break          
        
        # move to next page
        try:
            nextButton[0].click()
        except:
            break
        time.sleep(random.randrange(1, 2))

        counter += 1
        print('page: ' + str(counter))

save_main_file()
            