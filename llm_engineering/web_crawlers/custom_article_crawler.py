# we are going to use langchain to create a custom web crawler that can crawl articles from a website
# it takes AsyncHtmlLoader to read the entire HTML from a link then uses Html2TextTransformer to convert the HTML to text
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer
from loguru import logger

from urllib.parse import urlparse

from llm_engineering.pages.documents import ArticleDocument
from .base import BaseCrawler

# this way we don't need to use selenium or playwright to scrape the web pages
class CustomArticleCrawler(BaseCrawler):
    model = ArticleDocument

    # super class constructor grabs init method from BaseCrawler
    def __init__(self) -> None:
        super().__init__()

    # this method extracts the content from the link provided
    def extract(self, link: str, **kwargs) -> None:

        # first to check if the article already exists in the database
        # if it does, we don't need to scrape it again
        old_model = self.model.find(link=link) # remember the find methon checks based on a unique field, in this case the link
        if old_model is not None:
            logger.info(f"Article already exists in the database: {link}")
            return

        logger.info(f"Starting scrapping article: {link}")

        loader = AsyncHtmlLoader([link])
        docs = loader.load()

        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        doc_transformed = docs_transformed[0]

        # get the content from the transformed document
        # the content is a dictionary with the title, subtitle, content and language
        content = {
            "Title": doc_transformed.metadata.get("title"),
            "Subtitle": doc_transformed.metadata.get("description"),
            "Content": doc_transformed.page_content,
            "language": doc_transformed.metadata.get("language"),
        }

        # parse the link to get the platform
        # we use urlparse to get the netloc which is the domain of the link
        parsed_url = urlparse(link)
        platform = parsed_url.netloc

        # create an instance of the ArticleDocument model with the content, link, platform and user information
        # the user information is passed as a keyword argument
        user = kwargs["user"]
        instance = self.model(
            content=content,
            link=link,
            platform=platform,
            author_id=user.id,
            author_full_name=user.full_name,
        )
        # save the instance to the database
        # this will create a new document in the database with the content of the article
        instance.save()

        logger.info(f"Finished scrapping custom article: {link}")