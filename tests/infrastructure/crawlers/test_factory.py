from vedika.infrastructure.crawlers.github import GithubCrawler


def test_github_tree_url_keeps_selected_ref_and_canonicalizes_source() -> None:
    crawler = GithubCrawler(github_token=None)
    url = "https://github.com/sutr-am/vedika/tree/feature-engineering"

    assert crawler.canonicalize_url(url) == "https://github.com/sutr-am/vedika"
    assert crawler.get_ref(url) == "feature-engineering"
