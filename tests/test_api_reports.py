"""Testes de integracao da API de relatorios (PDF) do FrioVale.

Cobre: GET /api/reports/pdf (relatorio por motorista/periodo) e
GET /api/reports/trips/{id}/pdf (relatorio detalhado da viagem).
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
        pytest.skip("Nao foi possível autenticar para testes de relatorios")
    token = login_resp.json()["token"]
    return {**api_headers, "Authorization": f"Bearer {token}"}


class TestReportsPdf:
    """Testes de geracao de relatorios em PDF."""

    def test_trip_pdf(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/reports/trips/1/pdf",
            headers=headers,
            timeout=10,
        )
        # 200 com PDF ou 404 se a viagem nao existir
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.headers.get("Content-Type", "").startswith("application/pdf")

    def test_driver_report_pdf(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        params = {"mode": "driver", "month": "11", "year": "2026", "ids": "1"}
        response = requests.get(
            f"{api_base_url}/api/reports/pdf",
            headers=headers,
            params=params,
            timeout=10,
        )
        assert response.status_code in (200, 400, 404)
        if response.status_code == 200:
            assert response.headers.get("Content-Type", "").startswith("application/pdf")
