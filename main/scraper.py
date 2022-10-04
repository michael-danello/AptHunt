import time
import logging
# web scraping
from selenium import webdriver

from utils import log_time, delay_execution
from proxy_utils import get_new_proxy_server
import queries

class CaptchaError(Exception):
    pass


class StreetEasyScraper:
    
    def __init__(self, proxy):
        self.proxy = proxy
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % self.proxy)
        self.driver = webdriver.Chrome(options=chrome_options)

    @log_time
    @delay_execution(seconds=1)
    def get(self, url, retry=0):
        """Fetch a page"""
        self.driver.get(url)

        if not queries.has_captcha(self.driver):
            
            logging.info("Captcha Reached")

            if retry < 2:
                self.shuffle_proxy_server()
                self.get(url, retry=retry+1)

            else: 
                raise CaptchaError("Maximum Retries Exceeded")
        
    
    def shuffle_proxy_server(self):
        new_proxy = get_new_proxy_server()
        self.__init__(proxy=new_proxy)
            
        



    

    
    