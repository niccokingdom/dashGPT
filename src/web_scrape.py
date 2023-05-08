import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from text import *

# search online
from duckduckgo_search import ddg 
from googlesearch import search

def google_search(query: str, num_results: int = 3) -> str:
    """Returns urls for input search string
    """
    search_urls = []

    for j in search(query, tld="co.in", num=num_results, stop=num_results, pause=2):
        search_urls.append(j)

    return search_urls



def google_search_ddg(query: str, num_results: int = 3) -> str:
    """Returns urls for input search string
    """
    search_results = []

    results = ddg(query, max_results=num_results)
    for search in results:
        search_results.append(search['href'])
    

    return search_results



def scrape_text_with_selenium(url: str):
    """Scrape text from a website using selenium
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36"
    )
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Get the HTML content directly from the browser's DOM
    page_source = driver.execute_script("return document.body.outerHTML;")
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return driver, text.encode("utf-8").decode('utf-8')