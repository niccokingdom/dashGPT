from api import API
from utils import *
from text import *
from web_scrape import *
import logging

#import argparse

#parser = argparse.ArgumentParser(description='Description of your script')
#parser.add_argument('--variable', type=str, help='Description of your variable')

#args = parser.parse_args()
logger = logging.getLogger("log")
logging.basicConfig(level = logging.INFO)

objective = input("Select what you would like to explore\n")
n_articles = int(input("Select desired number of websites to visit\n"))
open_ai_key = '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'

header = f"""
Summarize this text with the following objective in mind: "{objective}":
Format The output with bullet points and add a recommendation based on your personal output and the one from the summary.

Text:
"""
gptAPI = API(open_ai_key=open_ai_key)
urls=[]
bodies=[]
summaries = []

google_searches = gptAPI.best_google_searches(objective)
logger.info(f"Objective:{objective}\nBest associated google queries:\n{google_searches}")

for search in google_searches:
    urls_tmp = list(set(google_search_ddg(search, 6))) # 6 urls per search
    for url_tmp in urls_tmp:
         if url_tmp not in urls:
              urls.append(url_tmp)
urls = urls[:n_articles]

logger.info(len(urls), " urls in total to webscrape, starting...\n")
#speak(f"{len(urls)} urls in total to webscrape, starting...\n")

for url in urls:
    
    logger.info(f"scraping body for: {url}")

    driver, body = scrape_text_with_selenium(url)
    bodies.append(body)


summary = gptAPI.summarise_texts(bodies, objective, 2000)
summaries.append(summary)
final_summary = header + "\n" + "\n".join(summaries)

logger.info(f"scraping body for: {url}")

with open('search_output.txt', 'w', encoding='utf-8') as file:
        file.write(final_summary + '\n')


logger.info("summary completed and search search_output.txt file generated")
#speak("summary completed and output file generated")

#speak('Here follows the summary:' + "\n".join(summaries))
