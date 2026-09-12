import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.rss_scraper import fetch_rss_posts

def get_leads():

    return fetch_rss_posts()