from selenium.webdriver.chrome.options import Options
from compatibledriver import ChromeDriver, SafariDriver
from crawler import Crawler

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

#TODO: LLM to find these
site_model = {
    'url' : f'https://www.upwork.com/nx/search/jobs/?nbs=1&page=1&q={keyword}&sort=recency',
    'items_sel' : "section[data-test='JobsList'] > article",
    'item_selectors' : {
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
    },
    'main_key' : "job_link",
    'next_pg_sel' : "button[data-ev-label='pagination_next_page']",
    'detail_open_sel' : "h2.job-tile-title a",
    'details_selectors' : {
        "location":'div.job-details-loader div[data-test="LocationLabel"]',
        "client_location": "div.job-details-loader li[data-qa='client-location']",
        "client_job_posting_stats": "div.job-details-loader li[data-qa='client-job-posting-stats']",
        "client_activity": 'div.job-details-loader ul.client-activity-items',
        "client_contract_date": 'div.job-details-loader div[data-qa="client-contract-date"]'
    },
    'detail_close_sel' : "button[data-test='slider-close-desktop']",
}

crawler = Crawler(driver, site_model, query=keyword)

crawler.run()
driver.quit()