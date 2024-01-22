from selenium.webdriver.chrome.options import Options
from compatibledriver import ChromeDriver, SafariDriver
from crawler import Crawler, RecordItems, Input
from datafile import print_err

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

driver = ChromeDriver(chrome_options, './chromedriver-mac-arm64/chromedriver')


if len(args.keyword)<1:
    print_err('Enter keyword: ',end='')
    keyword = input()
else:
    keyword = args.keyword

url = f'https://www.freelancer.com/jobs/?status=all'
#TODO: LLM to find these
actions=[
        Input(
            inputs=[
                {
                    "selector":"input#keyword-input",
                    "value":keyword
                }
            ],
            confirm_sel="button#search-submit"
        ),
        RecordItems(
            url = url,
            query = keyword,

            items_sel = "div.JobSearchCard-item",
            item_selectors = {
                "posted_time": "span.JobSearchCard-primary-heading-days",
                "job_title": "div.JobSearchCard-primary-heading a",
                "job_type": "div.JobSearchCard-secondary-price",
                #"experience_level": "li[data-test='experience-level']",
                #"duration_hours": "li[data-test='duration-label']",
                "prop": "div.JobSearchCard-secondary-entry",
                "job_description": "p.JobSearchCard-primary-description",
                "skill_tags": {
                    "selector":"div.JobSearchCard-primary-tags a",
                    "type": "multi-text"
                },
                "job_link": {
                    "selector": "div.JobSearchCard-primary-heading a[href]",
                    "type": "attr"
                }
            },
            main_key = "job_link",
            next_pg_sel = "li[data-link='next_page'] a",
        )
    ]

crawler = Crawler(driver, url = url, query=keyword, actions=actions)

crawler.run()
driver.quit()