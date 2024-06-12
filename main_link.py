import time
import random
import requests
from protego import Protego
from utility.config import *
from datetime import datetime, timedelta


class TimeOutHandler:
    def __init__(self) -> None:
        self.time_out_length = initial_timeout_length
        self.try_after = time.time()

    def correctly(self):
        self.time_out_length = initial_timeout_length
        self.try_after = time.time()

    def wrong(self):
        self.time_out_length = max(maximum_timeout_length, self.time_out_length * 2)
        self.try_after += self.try_after

    def is_available(self):
        return time.time() > self.try_after


class MainLink:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.rp = None
        self.delay = 0
        self._process_robots_txt()
        self.timeout_handler = TimeOutHandler()
        self.last_crawled = time.time() - 10

    def is_available(self):
        if not self.timeout_handler.is_available():
            return False
        if time.time() - self.last_crawled < self.delay:
            return False
        return True

    def handle_response_result(self, result: int, change=None):
        if result == -1 or result == -2:
            self.timeout_handler.wrong()
            print(f"{self.name} got timed-out for {self.timeout_handler.time_out_length}")

        elif result >= 500:
            self.timeout_handler.wrong()
            print(f"{self.name} got timed-out for {self.timeout_handler.time_out_length}")

        elif result == 429:
            self.timeout_handler.wrong()
            print(f"{self.name} got timed-out for {self.timeout_handler.time_out_length}")
            self.delay = max(self.delay * 2, maximum_delay)
            print(f"{self.name} delay is now {self.delay}")

        elif 400 <= result < 500:
            print('bad request!')
            
        elif 200 <= result < 300:
            self.timeout_handler.correctly()

    def is_allowed_for_robots(self, url):
        if self.ignore_robots_txt:
            return True
        return self.rp.can_fetch(url, user_agent="*")

    def _process_robots_txt(self):
        try:
            print(f'Checking robots.txt {self.url}')
            r = requests.get(self.url + "/robots.txt", timeout=10)
            r.raise_for_status()
        except:
            self.robots_txt = False
            self.ignore_robots_txt = True
            return
        self.robots_txt = True
        rules = r.text
        self.rp = Protego.parse(rules)

        t1 = 0
        t2 = 0
        if self.rp.request_rate("*") is not None:
            t1 = self.rp.request_rate("*").seconds / self.rp.request_rate("*").requests

        if self.rp.crawl_delay("*") is not None:
            t2 = self.rp.crawl_delay("*")

        t = max(t1, t2)

        self.delay = 1 if t == 0 else t

        self.ignore_robots_txt = not self.rp.can_fetch(url=self.url, user_agent="*")
        
    def get(self, url):
        if (not self.is_available()) or (not self.is_allowed_for_robots(url)):
            return None
        agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"
        headers = {'User-Agent': agent}
        response = self.session.get(url, headers=headers)
        self.handle_response_result(response.status_code)
        self.last_crawled = time.time()
        return response.text
    
    
        
