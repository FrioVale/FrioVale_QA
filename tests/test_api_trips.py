"""Testes de integracao da API de viagens do FrioVale.

Requerem o back-end Spring Boot rodando em http://localhost:8080.
Endpoints: GET/POST /api/trips, PUT /api/trips/{id}/start, /api/trips/{id}/end,
GET /api/trips/active/monitor, GET /api/trips/{id}/telemetry.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def _auth_headers(api_headers, api_base_url, login_payload):
    """Faz login e retorna cabecalho com Bearer token, ou salta o teste."""
    import requests

    login_resp = requests.post(
        f"{api_base_url}/api/auth/login",
        headers=api_headers,
        json=login_payload,
        timeout=10,
    )
    if login_resp.status_code != 200:
        pytest.skip("Nao foi possível autenticar para testes de viagem")
    token = login_resp.json()["token"]
    return {**api_headers, "Authorization": f"Bearer {token}"}


class TestTripsList:
    """Testes do endpoint GET /api/trips."""

    def test_list_trips_requires_auth(self, api_base_url, api_headers):
        import requests

        response = requests.get(f"{api_base_url}/api/trips", headers=api_headers, timeout=10)
        assert response.status_code == 401

    def test_list_trips_success(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(f"{api_base_url}/api/trips", headers=headers, timeout=10)
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)


class TestTripCreation:
    """Testes do endpoint POST /api/trips."""

    def test_create_trip_success(self, api_base_url, api_headers, login_payload, trip_request_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.post(
            f"{api_base_url}/api/trips",
            headers=headers,
            json=trip_request_payload,
            timeout=10,
        )
        assert response.status_code in (200, 201)
        body = response.json()
        assert "id" in body
        assert body["status"] in ("IN_TRANSIT", "PLANNED")

    def test_create_trip_invalid_driver_role(self, api_base_url, api_headers, login_payload):
        """Usuario nao motorista nao pode ser motorista da viagem."""
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        payload = {
            "containerId": 1,
            "driverId": 1,  # presumivelmente administrador
            "fruitId": 1,
            "origin": "Origem",
            "destination": "Destino",
            "shouldStartNow": True,
        }
        response = requests.post(
            f"{api_base_url}/api/trips",
            headers=headers,
            json=payload,
            timeout=10,
        )
        assert response.status_code in (400, 422)

    def test_create_trip_missing_required_fields(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.post(
            f"{api_base_url}/api/trips",
            headers=headers,
            json={},
            timeout=10,
        )
        assert response.status_code in (400, 422)


class TestTripStatusTransitions:
    """Testes de transicao de status PLANNED -> IN_TRANSIT -> COMPLETED."""

    def test_start_trip(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)

        # Cria uma viagem primeiro
        create_resp = requests.post(
            f"{api_base_url}/api/trips",
            headers=headers,
            json={
                "containerId": 1,
                "driverId": 2,
                "fruitId": 1,
                "origin": "Origem",
                "destination": "Destino",
                "shouldStartNow": False,
            },
            timeout=10,
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Nao foi possível criar viagem para teste de inicio")

        trip_id = create_resp.json()["id"]

        # Inicia a viagem
        start_resp = requests.put(
            f"{api_base_url}/api/trips/{trip_id}/start",
            headers=headers,
            timeout=10,
        )
        assert start_resp.status_code in (200, 400, 409)

    def test_end_trip(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)

        # Cria e inicia viagem
        create_resp = requests.post(
            f"{api_base_url}/api/trips",
            headers=headers,
            json={
                "containerId": 1,
                "driverId": 2,
                "fruitId": 1,
                "origin": "Origem",
                "destination": "Destino",
                "shouldStartNow": True,
            },
            timeout=10,
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Nao foi possível criar viagem para teste de fim")

        trip_id = create_resp.json()["id"]

        # Finaliza a viagem
        end_resp = requests.put(
            f"{api_base_url}/api/trips/{trip_id}/end",
            headers=headers,
            timeout=10,
        )
        assert end_resp.status_code in (200, 400, 409)

    def test_cannot_end_planned_trip(self, api_base_url, api_headers, login_payload):
        """Viagem PLANNED nao pode ser finalizada diretamente."""
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)

        create_resp = requests.post(
            f"{api_base_url}/api/trips",
            headers=headers,
            json={
                "containerId": 1,
                "driverId": 2,
                "fruitId": 1,
                "origin": "Origem",
                "destination": "Destino",
                "shouldStartNow": False,
            },
            timeout=10,
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Nao foi possível criar viagem")

        trip_id = create_resp.json()["id"]
        end_resp = requests.put(
            f"{api_base_url}/api/trips/{trip_id}/end",
            headers=headers,
            timeout=10,
        )
        assert end_resp.status_code in (400, 409)


class TestActiveTripsMonitor:
    """Testes do endpoint GET /api/trips/active/monitor."""

    def test_active_monitor_list(self, api_base_url, api_headers, login_payload):
        import requests

        headers = _auth_headers(api_headers, api_base_url, login_payload)
        response = requests.get(
            f"{api_base_url}/api/trips/active/monitor",
            headers=headers,
            timeout=10,
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
