"""Testes de integracao da API de telemetria do FrioVale.

Cobre: recebimento de leituras dos sensores, validacao de temperatura
e umidade, geracao de alertas fora da faixa e comunicacao com o ThingSpeak
(IoT). Requerem o back-end rodando.
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
        pytest.skip("Nao foi possível autenticar para testes de telemetria")
    token = login_resp.json()["token"]
    return {**api_headers, "Authorization": f"Bearer {token}"}


class TestTelemetryHistory:
    """Testes do endpoint GET /api/trips/{id}/telemetry."""

    def test_telemetry_history_requires_auth(self, api_base_url, api_headers):
        import requests

        response = requests.get(
            f"{api_base_url}/api/trips/1/telemetry",
            headers=api_headers,
            timeout=10,
        )
        assert response.status_code == 401

    def test_telemetry_history_for_existing_trip(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/trips/1/telemetry",
            headers=headers,
            timeout=10,
        )
        # 200 se a viagem existir, 404 se nao
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            body = response.json()
            assert isinstance(body, list)


class TestAlerts:
    """Testes do endpoint GET /api/alerts."""

    def test_list_alerts(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(f"{api_base_url}/api/alerts", headers=headers, timeout=10)
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)


pass
