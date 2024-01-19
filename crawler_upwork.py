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

main_csv_file = f'upwork-{keyword}.csv'
run_start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
temp_csv_file = f'upwork-{run_start_time}.csv'
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

url = f'https://www.upwork.com/nx/search/jobs/?nbs=1&page=1&q={keyword}&sort=recency'

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
    items_sel = "section[data-test='JobsList'] > article"
    item_selectors = {
        "posted_time": "div.job-tile-header small span:nth-of-type(2)",
        "job_title": "h2.job-tile-title a",
        "job_type": "li[data-test='job-type-label']",
        "experience_level": "li[data-test='experience-level']",
        "duration_hours": "li[data-test='duration-label']",
        "job_description": "div[data-test*='JobDescription'] p"
    }
    item_multi_selectors = {
        "skill_tags": "span[data-test='token'] span"
    }
    item_attr_selectors = {
        "job_link": "h2.job-tile-title a[href]"
    }
    next_pg_sel = "button[data-ev-label='pagination_next_page']"

    try:
        # wait content to be loaded
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, items_sel)))
    except:
        break
    print(f"{items_sel} found")

    items = driver.find_elements(By.CSS_SELECTOR, items_sel)
    for i in range(len(items)):
        el = items[i]
        #print(f"{i} ### {el.get_attribute('innerHTML')}")   #TODO: LLM to parse HTML
        '''            
0 ### <!----> <!----> <div class="d-flex job-tile-header" data-v-472a8b92=""><div class="d-flex flex-column job-tile-header-line-height flex-1 mr-4 mb-3 flex-wrap" data-v-1535c4e8="" data-v-472a8b92="" data-test="JobTileHeader"><small class="text-light mb-1" data-v-1535c4e8=""><span data-v-1535c4e8="">Posted</span> <span data-v-1535c4e8="">11 minutes ago</span></small> <div data-ev-sublocation="!line_clamp" class="air3-line-clamp-wrapper" style="--lines: 2; --line-clamp-expanded-height: false; --line-clamp-line-height: undefinedpx;" data-v-1535c4e8="" data-test="UpCLineClamp"><!----> <div id="air3-line-clamp-2" tabindex="-1" class="air3-line-clamp is-clamped"><h2 class="h5 mb-0 mr-2 job-tile-title" data-v-1535c4e8=""><a data-v-1535c4e8="" href="/jobs/WordPress-Graphics-Design-Art-Director_~01a28611581b6733f4/" class="up-n-link" data-test="UpLink">WordPress Graphics Design, UI/UX, Art Director</a></h2></div> <!----></div></div> <div class="d-flex job-tile-actions" data-v-472a8b92=""><!----> <!----></div></div> <div data-v-472a8b92=""><div data-v-472a8b92="" data-test="JobTileDetails"><!----> <ul class="job-tile-info-list text-base-sm mb-4" data-test="JobInfoFeatures"><li data-test="job-type-label"><strong>Hourly</strong></li> <li data-test="experience-level"><strong>Expert</strong></li> <!----> <li data-test="duration-label"><strong class="mr-1">
  Est. time:
</strong> <strong>1 to 3 months, 30+ hrs/week</strong></li></ul> <div data-ev-sublocation="!line_clamp" class="air3-line-clamp-wrapper clamp text-body-sm mb-3" style="--lines: 2; --line-clamp-expanded-height: false; --line-clamp-line-height: undefinedpx;" data-test="UpCLineClamp JobDescription"><!----> <div id="air3-line-clamp-3" tabindex="-1" class="air3-line-clamp is-clamped"><p class="mb-0">We are a UK based MNC healthcare IT company, Currently working on an <span class="highlight">AI</span> &amp; Automation based product. We are looking to create a modern website, Currently we are looking for Graphics, UI/UX, Art Director, Expert in WordPress and flow diagrams designer.
It will be each defined task and pre approved budget against your estimate. It would be continuous jobs and we can have continuous long term engagement too.</p></div> <!----></div> <div class="air3-token-container" data-v-052229ee="" data-test="TokenClamp JobAttrs"><!----> <span data-test="token" class="air3-token" data-v-052229ee=""><span data-v-052229ee="" class="">Mobile App Design</span></span><span data-test="token" class="air3-token" data-v-052229ee=""><span data-v-052229ee="" class="">App Design</span></span><span data-test="token" class="air3-token" data-v-052229ee=""><span data-v-052229ee="" class="">Adaptive Web Design</span></span><span data-test="token" class="air3-token" data-v-052229ee=""><span data-v-052229ee="" class="">Graphic Design</span></span><span data-test="token" class="air3-token" data-v-052229ee=""><span data-v-052229ee="" class="">Adobe Photoshop</span></span><span data-test="token" class="air3-token" data-v-052229ee=""><span data-v-052229ee="" class="">Web Design</span></span><span data-test="token" class="air3-token d-none" data-v-052229ee=""><span data-v-052229ee="" class="">Adobe Illustrator</span></span><span data-test="token" class="air3-token d-none" data-v-052229ee=""><span data-v-052229ee="" class="">User Interface Design</span></span><span data-test="token" class="air3-token d-none" data-v-052229ee=""><span data-v-052229ee="" class="">User Experience Design</span></span><span data-test="token" class="air3-token d-none" data-v-052229ee=""><span data-v-052229ee="" class="">Wireframing</span></span> <span data-v-052229ee="" class="air3-token">
+4
</span></div> <!----> <!----></div> <!----></div>
        '''
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
                #data[key] = el.find_element(By.CSS_SELECTOR, sel).get_attribute('href')
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
        time.sleep(random.randrange(1, 5))

        counter += 1
        print('page: ' + str(counter))

save_main_file()
            