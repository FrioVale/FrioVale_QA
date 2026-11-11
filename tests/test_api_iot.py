"""Testes de integracao da API de logs IoT / ThingSpeak do FrioVale.

Cobre: GET /api/thingspeak/logs e POST /api/thingspeak/logs/sync.
Requerem o back-end Spring Boot rodando.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def _auth_headers(api_headers, api_base_url, login_payload):
    import requests

    login_resp = requests.post(
        f"{api_base_url}/api/auth/login",
        headers=api_headers,
        json=login_payload,
        timeout=10,
    )
    if login_resp.status_code != 200:
        pytest.skip("Nao foi possível autenticar para testes IoT/ThingSpeak")
    token = login_resp.json()["token"]
    return {**api_headers, "Authorization": f"Bearer {token}"}


class TestIoTLogs:
    """Testes do endpoint GET /api/thingspeak/logs."""

    def test_iot_logs_list(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(f"{api_base_url}/api/thingspeak/logs", headers=headers, timeout=10)
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            body = response.json()
            assert isinstance(body, list)

    def test_iot_logs_filtered_by_container(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/thingspeak/logs?containerId=1",
            headers=headers,
            timeout=10,
        )
        assert response.status_code in (200, 404)


class TestIoTSync:
    """Testes do endpoint POST /api/thingspeak/logs/sync."""

    def test_sync_iot_logs(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.post(
            f"{api_base_url}/api/thingspeak/logs/sync?results=100",
            headers=headers,
            timeout=30,
        )
        # 200 se sincronizou, 502/503 se o ThingSpeak externo nao responder
        assert response.status_code in (200, 502, 503, 504)
        if response.status_code == 200:
            body = response.json()
            assert "saved" in body
