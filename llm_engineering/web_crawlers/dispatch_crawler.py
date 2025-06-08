import re
from urllib.parse import urlparse
from loguru import logger
from github_crawler import GithubCrawler
from base import BaseCrawler


# The CrawlerDispatcher class is defines to manage and dispatch crawler instances based on given URLS and their domains
# The constructor initialises an empty dictionary to hold the crawlers
class CrawlerDispatcher:
    def __init__(self) -> None:
        self._crawlers = {}

    # As we are using the builder creational pattern to instantiate and configure the dispatcher, 
    # we define a build() class method that returns an instance of the dispatcher:
    @classmethod
    def build(cls) -> "CrawlerDispatcher":
        dispatcher = cls()
        return dispatcher
    
    def register_github(self) -> "CrawlerDispatcher":
        self.register("https://github.com", GithubCrawler)
        return self

    # This method sets a crawler instance based on the URL provided.
    def register(self, domain: str, crawler: type[BaseCrawler]) -> None:
        parsed_domain = urlparse(domain)
        domain = parsed_domain.netloc

        self._crawlers[r"https://(www\.)?{}/*".format(re.escape(domain))] = crawler