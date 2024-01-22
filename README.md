<!-- ABOUT THE PROJECT -->
## About This Project

This is a mini web crawler project, it's can be used for crawling job search result on upwork.com and freelancer.com or your twitter/X timelines.

It's mainly built for the research of utilizing LLM to accomplish the data crawling tasks.

### Prerequisites

This is what you need to install to run this program
- python3
- pip
- Selenium Webdriver, e.g. [Chrome](https://googlechromelabs.github.io/chrome-for-testing/), [Safari](https://developer.apple.com/documentation/webkit/testing_with_webdriver_in_safari)

### How to use
```
#with Chrome
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/mac-arm64/chromedriver-mac-arm64.zip
unzip chromedriver-mac-arm64.zip
#or Safari
safaridriver --enable

pip install selenium
pip install pandas

python crawler_upwork.py
python crawler_freelancer.py
python crawler_twitter.py
```

To crawl some web sites like Twitter/X, you need to login in the pop-up browser window.
