import pytest
from datetime import datetime
from connectors import example_connectors


@pytest.mark.parametrize(
    "datatype",
    [
        "case_studies",
        "computational_resources",
        "educational_resources",
        "events",
        "presentations",
        "projects",
        "publications",
        "news",
        "organisations",
    ],
)
def test_fetch_happy_path(datatype: str):
    connector = example_connectors[datatype]
    resources = list(connector.fetch(from_incl=datetime.min, to_excl=datetime.max))
    assert len(resources) >= 1
    resource = resources[0]
    if hasattr(resource, "keywords"):  # otherwise, only tested that connector can run
        assert set(resource.keywords) == {"keyword1", "keyword2"}


@pytest.mark.parametrize(
    "datatype",
    [
        "case_studies",
        "computational_resources",
        "educational_resources",
        "events",
        "presentations",
        "projects",
        "publications",
        "news",
        "organisations",
    ],
)
def test_retry_happy_path(datatype: str):
    connector = example_connectors[datatype]
    resource = connector.retry("1")
    if hasattr(resource, "keywords"):  # otherwise, only tested that connector can run
        assert set(resource.keywords) == {"keyword1", "keyword2"}
