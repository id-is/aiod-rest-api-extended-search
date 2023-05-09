import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient
from datetime import datetime


from database.model.news import OrmNews
from platform_names import PlatformName

from unittest.mock import Mock
from authentication import keycloak_openid


def get_default_user():

    default_user = {
        "name": "test-user",
        "realm_access": {
            "roles": [
                "default-roles-dev",
                "offline_access",
                "uma_authorization",
            ]
        },
    }
    return default_user


def test_happy_path(client: TestClient, engine: Engine):

    user = get_default_user()
    user["realm_access"]["roles"].append("edit_aiod_resources")
    keycloak_openid.decode_token = Mock(return_value=user)

    date_format = "%Y-%m-%d"
    news = [
        OrmNews(
            platform=PlatformName.aiod,
            platform_identifier=None,
            title="n1",
            body="b1",
            section="s1",
            headline="h1",
            source="s1",
            date_modified=datetime.strptime("2023-03-21", date_format),
            alternative_headline="ah1",
            word_count=10,
        ),
        OrmNews(
            platform=PlatformName.aiod,
            platform_identifier=None,
            title="n2",
            body="b2",
            section="s2",
            headline="h2",
            source="s1",
            date_modified=datetime.strptime("2023-03-21", date_format),
            alternative_headline="ah2",
            word_count=10,
        ),
        OrmNews(
            platform=PlatformName.aiod,
            platform_identifier=None,
            title="n3",
            body="b3",
            section="s3",
            headline="h3",
            source="s1",
            date_modified=datetime.strptime("2023-03-21", date_format),
            alternative_headline="ah3",
            word_count=10,
        ),
    ]

    with Session(engine) as session:
        # Populate database
        session.add_all(news)
        session.commit()

    response = client.post(
        "/news",
        json={
            "title": "n2",
            "body": "b4",
            "section": "s3",
            "headline": "h5",
            "source": "s1",
            "date_modified": "2023-03-21T00:00:00",
            "alternative_headline": "ah1",
            "word_count": 10,
        },
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == "n2"
    assert response_json["body"] == "b4"
    assert response_json["headline"] == "h5"
    assert response_json["source"] == "s1"
    assert response_json["date_modified"] == "2023-03-21T00:00:00"
    assert response_json["alternative_headline"] == "ah1"
    assert response_json["word_count"] == 10
    assert response_json["identifier"] == 4
    assert len(response_json) == 15


@pytest.mark.parametrize(
    "title",
    ["\"'é:?", "!@#$%^&*()`~", "Ω≈ç√∫˜µ≤≥÷", "田中さんにあげて下さい", " أي بعد, ", "𝑻𝒉𝒆 𝐪𝐮𝐢𝐜𝐤", "گچپژ"],
)
def test_unicode(client: TestClient, engine: Engine, title):

    user = get_default_user()
    user["realm_access"]["roles"].append("edit_aiod_resources")
    keycloak_openid.decode_token = Mock(return_value=user)

    response = client.post(
        "/news",
        json={
            "title": title,
            "body": "b4",
            "section": "s3",
            "headline": "h5",
            "source": "s1",
            "date_modified": "2023-03-21T00:00:00",
            "alternative_headline": "ah1",
            "word_count": 10,
        },
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == title


@pytest.mark.parametrize(
    "field",
    [
        "title",
        "body",
        "section",
        "headline",
        "date_modified",
        "word_count",
    ],
)
def test_missing_value(client: TestClient, engine: Engine, field: str):

    user = get_default_user()
    user["realm_access"]["roles"].append("edit_aiod_resources")
    keycloak_openid.decode_token = Mock(return_value=user)

    data = {
        "title": "Title",
        "body": "b4",
        "section": "s3",
        "headline": "h5",
        "date_modified": "2023-03-21T00:00:00",
        "word_count": 10,
    }  # type: typing.Dict[str, typing.Any]
    del data[field]
    response = client.post("/news", json=data, headers={"Authorization": "fake-token"})
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"loc": ["body", field], "msg": "field required", "type": "value_error.missing"}
    ]


@pytest.mark.parametrize(
    "field",
    [
        "title",
        "body",
        "section",
        "headline",
        "date_modified",
        "word_count",
    ],
)
def test_null_value(client: TestClient, engine: Engine, field: str):

    user = get_default_user()
    user["realm_access"]["roles"].append("edit_aiod_resources")
    keycloak_openid.decode_token = Mock(return_value=user)

    data = {
        "title": "Title",
        "body": "b4",
        "section": "s3",
        "headline": "h5",
        "date_modified": "2023-03-21T00:00:00",
        "word_count": 10,
    }  # type: typing.Dict[str, typing.Any]
    data[field] = None
    response = client.post("/news", json=data, headers={"Authorization": "fake-token"})
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {
            "loc": ["body", field],
            "msg": "none is not an allowed value",
            "type": "type_error.none.not_allowed",
        }
    ]


def test_unauthorized_user(client: TestClient, engine: Engine):

    user = get_default_user()
    keycloak_openid.decode_token = Mock(return_value=user)

    response = client.post(
        "/news",
        json={
            "title": "title",
            "body": "b4",
            "section": "s3",
            "headline": "h5",
            "source": "s1",
            "date_modified": "2023-03-21T00:00:00",
            "alternative_headline": "ah1",
            "word_count": 10,
        },
        headers={"Authorization": "fake-token"},
    )
    assert response.status_code == 403
    response_json = response.json()
    assert response_json["detail"] == "You donot have permission to edit Aiod resources"


def test_unauthenticated_user(client: TestClient, engine: Engine):

    response = client.post(
        "/news",
        json={
            "title": "title",
            "body": "b4",
            "section": "s3",
            "headline": "h5",
            "source": "s1",
            "date_modified": "2023-03-21T00:00:00",
            "alternative_headline": "ah1",
            "word_count": 10,
        },
    )
    assert response.status_code == 401
    response_json = response.json()
    assert response_json["detail"] == "Not logged in"
