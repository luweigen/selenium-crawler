from selenium.webdriver.chrome.options import Options
from compatibledriver import ChromeDriver, SafariDriver
from crawler import Crawler, RecordItems, Input
from datafile import print_err

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--keyword', type=str, default='Following', help="keyword")
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

url = url = f'https://twitter.com/home'
#TODO: LLM to find these
actions=[
        Input(
            inputs=[
            ],
            confirm_sel='a[role="tab"][tabindex="-1"]',
            wait=3
        ),
        RecordItems(
            url = url,
            query = keyword,

            items_sel = "article[data-testid='tweet']",
            item_selectors = {
                "author":'div[data-testid="User-Name"]',#"div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)",
                "author_link":{
                    'selector':'div[data-testid="User-Name"] a[href]:nth-of-type(1)',
                    'type':'attr'
                },
                "item_link":{
                    'selector':'div[data-testid="User-Name"] > div:last-child > div > div:last-child > a[href]',
                    'type':'attr'
                },
                "posted_time":{
                    'selector':'div[data-testid="User-Name"] time[datetime]',
                    'type':'attr'
                },
                "text":'div[data-testid="tweetText"]',#"div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)", #or reply to
                "additional":{#image or reference tweet or text if above is reply to
                    "selector":"div[aria-labelledby]",
                    "type":"html"
                }
            },
            main_key = "item_link",
            second_key = "additional",
            #consecutive_duplicate = 5,
            next_pg_act = "scroll",
            storage="sql"
        )
    ]

crawler = Crawler(driver, url = url, query=keyword, actions=actions)

crawler.run()
driver.quit()