import os
import requests


BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8088")
VALID_TOKEN = os.getenv("TEST_VALID_TOKEN", "valid-demo-token")


def test_health():
    response = requests.get(
        f"{BASE_URL}/health",
        timeout=5,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["database"] == "connected"


def test_invalid_token_returns_401():
    response = requests.get(
        f"{BASE_URL}/api/v1/account",
        headers={
            "Authorization": "Bearer expired-demo-token",
        },
        timeout=5,
    )

    assert response.status_code == 401

    body = response.json()

    assert body["error"] == "unauthorized"
    assert "request_id" in body


def test_valid_token_returns_account():
    response = requests.get(
        f"{BASE_URL}/api/v1/account",
        headers={
            "Authorization": f"Bearer {VALID_TOKEN}",
        },
        timeout=5,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["account_id"] == "acct_demo_001"
    assert body["status"] == "active"


def test_provider_configuration_failure_and_recovery():
    provider_id = "provider_demo_001"

    disable = requests.post(
        f"{BASE_URL}/api/v1/admin/providers/{provider_id}/callback",
        json={
            "enabled": False,
        },
        timeout=5,
    )

    assert disable.status_code == 200
    assert disable.json()["callback_enabled"] is False

    failed = requests.post(
        f"{BASE_URL}/api/v1/provider/session",
        timeout=5,
    )

    assert failed.status_code == 403

    failed_body = failed.json()

    assert failed_body["error"] == "integration_error"

    enable = requests.post(
        f"{BASE_URL}/api/v1/admin/providers/{provider_id}/callback",
        json={
            "enabled": True,
        },
        timeout=5,
    )

    assert enable.status_code == 200
    assert enable.json()["callback_enabled"] is True

    recovered = requests.post(
        f"{BASE_URL}/api/v1/provider/session",
        timeout=5,
    )

    assert recovered.status_code == 200
    assert recovered.json()["status"] == "created"


def test_frontend_and_backoffice_are_available():
    frontend = requests.get(
        f"{BASE_URL}/",
        timeout=5,
    )

    backoffice = requests.get(
        f"{BASE_URL}/admin/",
        timeout=5,
    )

    assert frontend.status_code == 200
    assert "Acme Gaming Account Portal" in frontend.text

    assert backoffice.status_code == 200
    assert "Provider Integration Back Office" in backoffice.text
