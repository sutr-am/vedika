# src/vedika/infrastructure/crawlers/github.py
import hashlib
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse
from uuid import UUID, uuid5

from github import Auth, Github
from github.GithubException import GithubException
from loguru import logger
from pydantic import HttpUrl
from tqdm import tqdm

from vedika.application.interfaces.crawlers import BaseCrawler
from vedika.domain.raw import CodebaseRawDomain
from vedika.domain.types import DataCategory


class GithubCrawler(BaseCrawler):
    category: DataCategory = DataCategory.CODEBASES
    provider = "github"
    version = "1"

    def __init__(
        self,
        token: str | None,
        ignore=(
            ".git",
            ".toml",
            ".lock",
            ".png",
            ".jpg",
            "__pycache__",
            ".gitignore",
            ".DS_Store",
        ),
    ) -> None:
        # super().__init__(repository)
        self._ignore = ignore
        if token:
            auth = Auth.Token(token=token)
            self.gh = Github(auth=auth)
        else:
            self.gh = Github()

    def canonicalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname != "github.com":
            raise ValueError(f"Invalid GitHub repository URL: {url}")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError(f"GitHub repository URL must include owner and repository: {url}")
        owner, repository = parts[:2]
        return f"https://github.com/{owner.lower()}/{repository.removesuffix('.git').lower()}"

    @staticmethod
    def _parse_repo_url(canonical_url: str) -> tuple[str, str]:
        repo_path = urlparse(canonical_url).path.strip("/")
        return repo_path, repo_path.split("/")[-1]

    def get_ref(self, url: str) -> str | None:
        parts = [part for part in urlparse(url).path.split("/") if part]
        if len(parts) > 3 and parts[2] == "tree":
            return "/".join(parts[3:])
        return None

    def get_revision(self, canonical_url: str, ref: str | None) -> str:
        repo_path, _ = self._parse_repo_url(canonical_url)
        repo = self.gh.get_repo(repo_path)
        return repo.get_branch(ref or repo.default_branch).commit.sha

    def _should_ignore(self, file_path: str) -> bool:
        path_parts = file_path.split("/")
        return any(file_path.endswith(ignore) or ignore in path_parts for ignore in self._ignore)

    @staticmethod
    def _get_blob_shas(repository_path: Path) -> dict[str, str]:
        result = subprocess.run(
            ["git", "-C", str(repository_path), "ls-tree", "-r", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        blob_shas = {}
        for line in result.stdout.splitlines():
            metadata, file_path = line.split("\t", maxsplit=1)
            blob_shas[file_path] = metadata.split()[2]
        return blob_shas

    def _build_documents(
        self,
        repository_path: Path,
        repository_name: str,
        user_id: UUID,
        source_id: UUID,
        crawl_id: UUID,
        canonical_url: str,
        blob_shas: dict[str, str],
    ) -> list[CodebaseRawDomain]:
        documents = []
        files = [path for path in repository_path.rglob("*") if path.is_file()]
        for file_path in tqdm(files, desc=f"Crawling {repository_name} files"):
            relative_path = file_path.relative_to(repository_path).as_posix()
            if self._should_ignore(relative_path):
                continue
            try:
                file_content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                logger.warning(f"Skipped file {relative_path} due to error: {error}")
                continue

            if file_content:
                documents.append(
                    CodebaseRawDomain(
                        id=uuid5(crawl_id, relative_path),
                        source_id=source_id,
                        crawl_id=crawl_id,
                        title=f"github/{repository_name}/{relative_path}",
                        content=file_content,
                        platform="github",
                        source_url=HttpUrl(canonical_url),
                        user_id=user_id,
                        repository_path=relative_path,
                        upstream_file_sha=blob_shas.get(relative_path, ""),
                        content_sha256=hashlib.sha256(file_content.encode()).hexdigest(),
                    )
                )
        return documents

    @staticmethod
    def _clone_repository(canonical_url: str, ref: str, destination: Path) -> None:
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--no-tags",
                    "--single-branch",
                    "--branch",
                    ref,
                    canonical_url,
                    str(destination),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            details = error.stderr.strip() or error.stdout.strip()
            raise RuntimeError(f"Unable to clone {canonical_url}: {details}") from error

    def extract(
        self, canonical_url: str, ref: str | None, user_id: UUID, source_id: UUID, crawl_id: UUID
    ) -> list[CodebaseRawDomain]:
        """
        Orchestrates the crawling process and saves the resulting CodebaseDocument
        """
        logger.info(f"Crawling Github Repository: {canonical_url}")

        repo_path, _ = self._parse_repo_url(canonical_url=canonical_url)
        try:
            repo = self.gh.get_repo(repo_path)
            clone_ref = ref or repo.default_branch
            with TemporaryDirectory(prefix="vedika-github-") as temporary_directory:
                checkout_path = Path(temporary_directory) / repo.name
                self._clone_repository(
                    canonical_url=canonical_url,
                    ref=clone_ref,
                    destination=checkout_path,
                )
                blob_shas = self._get_blob_shas(repository_path=checkout_path)
                return self._build_documents(
                    repository_path=checkout_path,
                    repository_name=repo.full_name,
                    user_id=user_id,
                    source_id=source_id,
                    crawl_id=crawl_id,
                    canonical_url=canonical_url,
                    blob_shas=blob_shas,
                )
        except GithubException as e:
            logger.exception(f"Failed to crawl {canonical_url}: {e}")
            raise e
