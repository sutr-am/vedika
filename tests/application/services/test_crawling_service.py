from unittest.mock import MagicMock
from uuid import UUID, uuid4

from vedika.application.services.crawling_service import CrawlerService
from vedika.domain.raw import CodebaseRawDomain
from vedika.domain.sources import CrawlDomain, SourceDomain
from vedika.domain.types import CrawlStatus, DataCategory


def build_document(user_id: UUID, source_id: UUID, crawl_id: UUID) -> CodebaseRawDomain:
    return CodebaseRawDomain(
        id=uuid4(),
        source_id=source_id,
        crawl_id=crawl_id,
        title="github/acme/widgets/main.py",
        content="print('hello')\n",
        platform="github",
        source_url="https://github.com/acme/widgets",
        user_id=user_id,
        repository_path="main.py",
        upstream_file_sha="upstream-sha",
        content_sha256="content-sha",
    )


def test_crawl_persists_file_documents_with_source_and_crawl_lineage() -> None:
    user_id = uuid4()
    source_id = uuid4()
    crawl_id = uuid4()
    crawler = MagicMock()
    crawler.category = DataCategory.CODEBASES
    crawler.provider = "github"
    crawler.version = "1"
    crawler.canonicalize_url.return_value = "https://github.com/acme/widgets"
    crawler.get_ref.return_value = None
    crawler.get_revision.return_value = "commit-sha"
    document = build_document(user_id, source_id, crawl_id)
    crawler.extract.return_value = [document]

    router = MagicMock()
    router.get_crawler.return_value = crawler
    source_repository = MagicMock()
    source_repository.get_or_create.return_value = SourceDomain(
        id=source_id,
        user_id=user_id,
        provider="github",
        canonical_url="https://github.com/acme/widgets",
    )
    crawl_repository = MagicMock()
    crawl_repository.get_successful.return_value = None
    crawl_repository.get_or_create.return_value = CrawlDomain(
        id=crawl_id,
        source_id=source_id,
        requested_url="https://github.com/acme/widgets/",
        canonical_url="https://github.com/acme/widgets",
        revision="commit-sha",
        crawler_version="1",
    )
    raw_repository = MagicMock()
    provider = MagicMock()
    provider.get_source_repository.return_value = source_repository
    provider.get_crawl_repository.return_value = crawl_repository
    provider.get_raw_repository.return_value = raw_repository

    status = CrawlerService(router, provider).crawl_and_save(
        url="https://github.com/acme/widgets/", user_id=user_id
    )

    assert status is CrawlStatus.SUCCESS
    crawler.extract.assert_called_once_with(
        canonical_url="https://github.com/acme/widgets",
        ref=None,
        user_id=user_id,
        source_id=source_id,
        crawl_id=crawl_id,
    )
    persisted_crawl_id, persisted_documents = (
        raw_repository.replace_crawl_documents.call_args.kwargs.values()
    )
    assert persisted_crawl_id == crawl_id
    assert persisted_documents == [document]
    assert persisted_documents[0].source_id == source_id
    assert persisted_documents[0].crawl_id == crawl_id
    crawl_repository.mark_succeeded.assert_called_once_with(crawl_id=crawl_id, document_count=1)


def test_crawl_skips_existing_successful_source_revision() -> None:
    user_id = uuid4()
    source_id = uuid4()
    crawl_id = uuid4()
    crawler = MagicMock()
    crawler.category = DataCategory.CODEBASES
    crawler.provider = "github"
    crawler.version = "1"
    crawler.canonicalize_url.return_value = "https://github.com/acme/widgets"
    crawler.get_ref.return_value = None
    crawler.get_revision.return_value = "commit-sha"
    router = MagicMock()
    router.get_crawler.return_value = crawler
    source_repository = MagicMock()
    source_repository.get_or_create.return_value = SourceDomain(
        id=source_id,
        user_id=user_id,
        provider="github",
        canonical_url="https://github.com/acme/widgets",
    )
    crawl_repository = MagicMock()
    crawl_repository.get_successful.return_value = CrawlDomain(
        id=crawl_id,
        source_id=source_id,
        requested_url="https://github.com/acme/widgets",
        canonical_url="https://github.com/acme/widgets",
        revision="commit-sha",
        crawler_version="1",
        status=CrawlStatus.SUCCESS,
        document_count=1,
    )
    raw_repository = MagicMock()
    raw_repository.has_crawl_documents.return_value = True
    provider = MagicMock()
    provider.get_source_repository.return_value = source_repository
    provider.get_crawl_repository.return_value = crawl_repository
    provider.get_raw_repository.return_value = raw_repository

    status = CrawlerService(router, provider).crawl_and_save(
        url="https://github.com/acme/widgets", user_id=user_id
    )

    assert status is CrawlStatus.SKIPPED
    crawler.extract.assert_not_called()
    provider.get_raw_repository.assert_called_once_with(category=DataCategory.CODEBASES)
    raw_repository.has_crawl_documents.assert_called_once_with(
        crawl_id=crawl_id,
        expected_count=1,
    )


def test_crawl_recrawls_when_successful_crawl_documents_are_missing() -> None:
    user_id = uuid4()
    source_id = uuid4()
    crawl_id = uuid4()
    crawler = MagicMock()
    crawler.category = DataCategory.CODEBASES
    crawler.provider = "github"
    crawler.version = "1"
    crawler.canonicalize_url.return_value = "https://github.com/acme/widgets"
    crawler.get_ref.return_value = None
    crawler.get_revision.return_value = "commit-sha"
    crawler.extract.return_value = []

    router = MagicMock()
    router.get_crawler.return_value = crawler
    source_repository = MagicMock()
    source_repository.get_or_create.return_value = SourceDomain(
        id=source_id,
        user_id=user_id,
        provider="github",
        canonical_url="https://github.com/acme/widgets",
    )
    crawl_repository = MagicMock()
    crawl_repository.get_successful.return_value = CrawlDomain(
        id=crawl_id,
        source_id=source_id,
        requested_url="https://github.com/acme/widgets",
        canonical_url="https://github.com/acme/widgets",
        revision="commit-sha",
        crawler_version="1",
        status=CrawlStatus.SUCCESS,
        document_count=3,
    )
    crawl_repository.get_or_create.return_value = CrawlDomain(
        id=crawl_id,
        source_id=source_id,
        requested_url="https://github.com/acme/widgets",
        canonical_url="https://github.com/acme/widgets",
        revision="commit-sha",
        crawler_version="1",
        status=CrawlStatus.RUNNING,
    )
    raw_repository = MagicMock()
    raw_repository.has_crawl_documents.return_value = False
    provider = MagicMock()
    provider.get_source_repository.return_value = source_repository
    provider.get_crawl_repository.return_value = crawl_repository
    provider.get_raw_repository.return_value = raw_repository

    status = CrawlerService(router, provider).crawl_and_save(
        url="https://github.com/acme/widgets", user_id=user_id
    )

    assert status is CrawlStatus.SUCCESS
    raw_repository.has_crawl_documents.assert_called_once_with(crawl_id=crawl_id, expected_count=3)
    crawler.extract.assert_called_once()
    raw_repository.replace_crawl_documents.assert_called_once_with(crawl_id=crawl_id, documents=[])
