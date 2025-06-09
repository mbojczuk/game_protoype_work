import os
import shutil
import subprocess
import tempfile
from loguru import logger
from .base import BaseCrawler
from llm_engineering.pages.documents import RepositoryDocument

# class that extends the BaseCrawler class
class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    def __init__( self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__() # Initialize the base class
        self._ignore = ignore # this is a tuple of file extensions to ignore

    # now to override the extract method
    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Repository already exists in the database: {link}")
            return

        logger.info(f"Starting scrapping GitHub repository: {link}")

        # Extract the repository name from the link
        repo_name = link.rstrip("/").split("/")[-1]
        # Create a temporary directory to clone the repository
        local_temp = tempfile.mkdtemp()

        try:
            # change the current working directory to the temporary directory
            logger.info(f"Cloning repository {repo_name} into temporary directory.")
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            # Check if the repository was cloned successfully
            if not os.listdir(local_temp):
                logger.error(f"Failed to clone repository {repo_name}. The directory is empty.")
                return
            
            # Log the successful cloning of the repository
            logger.info(f"Repository {repo_name} cloned successfully.")
            # Get the path of the cloned repository
            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])  # noqa: PTH118


            # For each relevant file, it reads the content, removes any spaces, 
            # and stores it in the dictionary with the file path as the key:
            tree = {}
            for root, _, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)  # noqa: PTH118
                    with open(os.path.join(root, file), "r", errors="ignore") as f:  # noqa: PTH123, PTH118
                        tree[file_path] = f.read().replace(" ", "")

            user = kwargs["user"]
            # Create an instance of the model with the scraped content and save it to the database
            logger.info(f"Creating database entry for repository {repo_name}.")
            instance = self.model(
                content=tree,
                name=repo_name,
                link=link,
                platform="github",
                author_id=user.id,
                author_full_name=user.full_name,
            )
            instance.save()

            logger.info(f"Finished scrapping GitHub repository: {link}")
        finally:
            shutil.rmtree(local_temp)  # Clean up the temporary directory
            logger.info(f"Temporary directory {local_temp} removed.")
            logger.info(f"Finished processing repository {repo_name}.")