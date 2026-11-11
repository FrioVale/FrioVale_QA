"""Testes de integracao do dashboard e usuarios do FrioVale.

Cobre: resumo do dashboard (metricas operacionais), gestao de equipe
(CRUD de usuarios) e estatisticas de motoristas.
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
        pytest.skip("Nao foi possível autenticar para testes de dashboard/usuarios")
    token = login_resp.json()["token"]
    return {**api_headers, "Authorization": f"Bearer {token}"}


class TestDashboard:
    """Testes do endpoint GET /api/dashboard/summary."""

    def test_dashboard_summary(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/dashboard/summary",
            headers=headers,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert "activeTrips" in body
        assert "tripsInRange" in body
        assert "activeAlerts" in body
        assert "activeDrivers" in body
        assert "trips" in body
        assert "recentAlerts" in body


class TestUsers:
    """Testes de gestao de usuarios (equipe FrioVale)."""

    def test_list_users(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(f"{api_base_url}/api/users", headers=headers, timeout=10)
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)

    def test_list_users_by_role(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/users?role=ROLE_DRIVER",
            headers=headers,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        for user in body:
            assert user["role"] == "ROLE_DRIVER"

    def test_create_user(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        payload = {
            "name": "Usuario Teste Automatizado",
            "email": f"teste.auto.{__import__('uuid').uuid4().hex[:8]}@friovale.com.br",
            "role": "ROLE_DRIVER",
        }
        response = requests.post(
            f"{api_base_url}/api/users",
            headers=headers,
            json=payload,
            timeout=10,
        )
        assert response.status_code in (200, 201)
        body = response.json()
        assert body["name"] == payload["name"]
        assert body["email"] == payload["email"]


class TestDriverStats:
    """Testes do endpoint GET /api/reports/drivers."""

    def test_driver_stats(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/reports/drivers",
            headers=headers,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
