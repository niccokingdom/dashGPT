from collections import deque

def get_unique_url(urls_deque, urls_list):
    while urls_deque:
        url = urls_deque.popleft()
        if url not in urls_list:
            return url
    return None