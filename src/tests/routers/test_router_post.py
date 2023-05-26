from unittest.mock import Mock

import pytest
from starlette.testclient import TestClient

from authentication import keycloak_openid


@pytest.mark.parametrize(
    "title",
    ["\"'é:?", "!@#$%^&*()`~", "Ω≈ç√∫˜µ≤≥÷", "田中さんにあげて下さい", " أي بعد, ", "𝑻𝒉𝒆 𝐪𝐮𝐢𝐜𝐤", "گچپژ"],
)
def test_unicode(client_test_resource: TestClient, title: str, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    response = client_test_resource.post(
        "/test_resources/v0",
        json={"title": title, "platform": "example", "platform_identifier": "1"},
        headers={"Authorization": "Fake token"},
    )
    assert response.status_code == 200
    assert response.json() == {"identifier": 1}
    response = client_test_resource.get("/test_resources/v0/1")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["title"] == title


def test_duplicated_resource(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    body = {"title": "title", "platform": "example", "platform_identifier": "1"}
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 200
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 409
    assert (
        response.json()["detail"] == "There already exists a test_resource with the same platform "
        "and name, with identifier=1."
    )


def test_missing_value(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    body = {"platform": "example", "platform_identifier": "1"}
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"loc": ["body", "title"], "msg": "field required", "type": "value_error.missing"}
    ]


def test_null_value(client_test_resource: TestClient, mocked_privileged_token: Mock):
    keycloak_openid.decode_token = mocked_privileged_token
    body = {"title": None, "platform": "example", "platform_identifier": "1"}
    response = client_test_resource.post(
        "/test_resources/v0", json=body, headers={"Authorization": "Fake token"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {
            "loc": ["body", "title"],
            "msg": "none is not an allowed value",
            "type": "type_error.none.not_allowed",
        }
    ]
