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
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_string(objective,n_articles, open_ai_key):
     
    # Clear Logs
    try:
         with open('app.log', 'w', encoding='utf-8') as file:
            file.truncate()
    except:
         pass

    header = f"""
    Summarize this text with the following objective in mind: "{objective}":
    Format The output with bullet points and add a recommendation based on your personal output and the one from the summary.

    Text:
    """
    gptAPI = API(open_ai_key=open_ai_key)
    urls=[]
    url_deques = []
    bodies=[]
    summaries = []

    google_searches = gptAPI.best_google_searches(objective)
    logger.info("\n\n************ New Search ************\n\n")
    logger.info(f"Objective:{objective}\nBest associated google queries:\n{google_searches}")

    # Collect URLs from each search, and store them in a list of deques
    for search in google_searches:
        urls_tmp = list(set(google_search_ddg(search, int(n_articles/3) + 10))) # In case of duplicated websites
        url_deques.append(deque(urls_tmp))

    # Loop through the list of deques and get one URL from each search until the desired number of articles is reached
    while len(urls) < n_articles and any(url_deques):
        for url_deque in url_deques:
            unique_url = get_unique_url(url_deque, urls)
            if unique_url:
                urls.append(unique_url)
            if len(urls) >= n_articles:
                break
    

    logger.info(len(urls), " urls in total to webscrape, starting...\n")

    for url in urls:
        
        logger.info(f"scraping body for: {url}")

        driver, body = scrape_text_with_selenium(url)
        bodies.append(body)


    summary = gptAPI.summarise_texts(bodies, objective, 3900)
    summaries.append(summary)
    final_summary = header + "\n" + "\n".join(summaries)

    with open('search_output.txt', 'w', encoding='utf-8') as file:
            file.write(final_summary + '\n')


    logger.info("summary completed and search search_output.txt file generated")

    return final_summary