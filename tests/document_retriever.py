from llm_engineering.web_crawlers.dispatch_crawler import CrawlerDispatcher
from llm_engineering.pages.documents import UserDocument
from typing_extensions import Annotated
from urllib.parse import urlparse
import yaml

from loguru import logger

from tqdm import tqdm

# This function tests the CrawlerDispatcher by registering a GitHub crawler and retrieving it.
def test_crawler_dispatcher(user: UserDocument, links: list[str]) -> Annotated[list[str], "crawled_links"]:

    # Create an instance of CrawlerDispatcher and register the GitHub crawler (can also register other crawlers)
    dispatcher = CrawlerDispatcher.build().register_github()

    logger.info(f"Starting to test the CrawlerDispatcher with {len(links)} link(s).")
    metadata = {}
    successful_crawls = 0
    for link in tqdm(links):
        successful_crawl, crawled_domain = _crawler_link(dispatcher, link, user)
        successful_crawls += successful_crawl

        metadata = _add_to_metadata(metadata, crawled_domain, successful_crawl)

    summary = {
        "total": len(links),
        "successful": successful_crawls,
        "failed": len(links) - successful_crawls,
        "metadata": metadata
    }

    logger.info(f"Finished testing the CrawlerDispatcher.")
    return summary


def _crawler_link(dispatcher: CrawlerDispatcher, link: str, user: UserDocument) -> tuple[bool, str]:
    crawler = dispatcher.get_crawler(link)
    crawler_domain = urlparse(link).netloc

    try:
        crawler.extract(link=link, user=user)

        return (True, crawler_domain)
    except Exception as e:
        logger.error(f"An error occurred while crowling: {e!s}")

        return (False, crawler_domain)


def _add_to_metadata(metadata: dict, domain: str, successfull_crawl: bool) -> dict:
    if domain not in metadata:
        metadata[domain] = {}
    metadata[domain]["successful"] = metadata[domain].get("successful", 0) + successfull_crawl
    metadata[domain]["total"] = metadata[domain].get("total", 0) + 1

    return metadata

def load_config(config_path: str) -> dict:
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def run_crawler():
    config = load_config("llm_engineering/configs/data_etl_michael.yaml")  # Load YAML

    # Extract first and last name from full_name
    full_name = config["parameters"]["user_full_name"]
    first_name, last_name = full_name.split(" ", 1)  # Splits at first space

    # Pass separate first_name and last_name fields
    user = UserDocument(first_name=first_name, last_name=last_name)
    links = config["parameters"]["links"]

    logger.info("Starting Crawler...")
    result = test_crawler_dispatcher(user, links)

    logger.info(f"Crawler Summary: {result}")

if __name__ == "__main__":
    run_crawler()
