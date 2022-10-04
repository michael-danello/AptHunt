from scraper import StreetEasyScraper
from proxy_utils import get_new_proxy_server

"""
Set up a databae connection 

pipe data in 
"""
proxy = get_new_proxy_server()
scraper = StreetEasyScraper(proxy=proxy)
scraper.get("https://www.google.com/")