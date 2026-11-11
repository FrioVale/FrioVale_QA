"""Testes de integracao da API de autenticacao do FrioVale.

Requerem o back-end Spring Boot rodando em http://localhost:8080.
Marcados com @pytest.mark.integration.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


class TestAuthLogin:
    """Testes do endpoint POST /api/auth/login."""

    def test_login_success(self, api_base_url, api_headers, login_payload):
        import requests

        response = requests.post(
            f"{api_base_url}/api/auth/login",
            headers=api_headers,
            json=login_payload,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert "token" in body
        assert "tokenType" in body
        assert "user" in body
        assert body["user"]["email"] == login_payload["email"]

    def test_login_invalid_credentials(self, api_base_url, api_headers):
        import requests

        response = requests.post(
            f"{api_base_url}/api/auth/login",
            headers=api_headers,
            json={"email": "naoexiste@friovale.com.br", "password": "senhaerrada"},
            timeout=10,
        )
        assert response.status_code in (401, 403)

    def test_login_missing_fields(self, api_base_url, api_headers):
        import requests

        response = requests.post(
            f"{api_base_url}/api/auth/login",
            headers=api_headers,
            json={},
            timeout=10,
        )
        assert response.status_code in (400, 422, 500)

    def test_login_success_admin_bootstrap(self, api_base_url, api_headers, admin_login_payload):
        """Login do administrador bootstrap (credenciais do properties).

        Deve retornar 200 com token se o back-end estiver rodando com as
        propriedades de bootstrap carregadas.
        """
        import requests

        response = requests.post(
            f"{api_base_url}/api/auth/login",
            headers=api_headers,
            json=admin_login_payload,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert "token" in body
        assert "tokenType" in body
        assert "user" in body
        assert body["user"]["email"] == admin_login_payload["email"]
        assert body["user"]["role"] == "ROLE_COMPANY"


class TestAuthRegister:
    """Testes do endpoint POST /api/auth/register."""

    def test_register_success(self, api_base_url, api_headers, register_payload):
        import requests

        response = requests.post(
            f"{api_base_url}/api/auth/register",
            headers=api_headers,
            json=register_payload,
            timeout=10,
        )
        assert response.status_code in (200, 201)
        body = response.json()
        assert "token" in body
        assert body["user"]["email"] == register_payload["email"]
        assert body["user"]["name"] == register_payload["name"]

    def test_register_duplicate_email(self, api_base_url, api_headers, register_payload):
        import requests

        # Primeiro cadastro
        requests.post(
            f"{api_base_url}/api/auth/register",
            headers=api_headers,
            json=register_payload,
            timeout=10,
        )
        # Segundo cadastro com mesmo email deve falhar
        response = requests.post(
            f"{api_base_url}/api/auth/register",
            headers=api_headers,
            json=register_payload,
            timeout=10,
        )
        assert response.status_code in (400, 409, 422)

    def test_register_invalid_email(self, api_base_url, api_headers):
        import requests

        payload = {
            "name": "Usuario Invalido",
            "email": "nao-e-um-email",
            "password": "senha123",
        }
        response = requests.post(
            f"{api_base_url}/api/auth/register",
            headers=api_headers,
            json=payload,
            timeout=10,
        )
        assert response.status_code in (400, 422)

    def test_register_password_too_short(self, api_base_url, api_headers):
        import requests

        payload = {
            "name": "Usuario Curto",
            "email": "curto@friovale.com.br",
            "password": "123",
        }
        response = requests.post(
            f"{api_base_url}/api/auth/register",
            headers=api_headers,
            json=payload,
            timeout=10,
        )
        assert response.status_code in (400, 422)


class TestAuthCurrentUser:
    """Testes do endpoint GET /api/users/current."""

    def test_current_user_requires_auth(self, api_base_url, api_headers):
        import requests

        response = requests.get(
            f"{api_base_url}/api/users/current",
            headers=api_headers,
            timeout=10,
        )
        # Sem token Bearer, deve retornar 401
        assert response.status_code == 401

    def test_current_user_with_token(self, api_base_url, api_headers, login_payload):
        import requests

        # Faz login para obter token
        login_resp = requests.post(
            f"{api_base_url}/api/auth/login",
            headers=api_headers,
            json=login_payload,
            timeout=10,
        )
        if login_resp.status_code != 200:
            pytest.skip("Nao foi possível autenticar para teste de usuario atual")

        token = login_resp.json()["token"]
        auth_headers = {**api_headers, "Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{api_base_url}/api/users/current",
            headers=auth_headers,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert "id" in body
        assert "email" in body
        assert "role" in body
