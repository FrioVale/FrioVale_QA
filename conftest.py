"""Fixtures globais para os testes automatizados do FrioVale."""

from __future__ import annotations

import os
from typing import Any

import pytest
import requests
from faker import Faker

fake = Faker("pt_BR")

# ---------------------------------------------------------------------------
# Configuracao da API
# ---------------------------------------------------------------------------

DEFAULT_API_BASE = "http://localhost:8080"


def _server_available(base_url: str, timeout: float = 2.0) -> bool:
    """Verifica se o back-end Spring Boot esta acessivel."""
    try:
        requests.get(f"{base_url}/api/trips", timeout=timeout)
        return True
    except requests.RequestException:
        return False


@pytest.fixture(scope="session")
def api_available(api_base_url: str) -> bool:
    """Indica se o back-end esta rodando (True) ou nao (False)."""
    return _server_available(api_base_url)


@pytest.fixture(autouse=True)
def _skip_integration_without_server(api_available: bool, request):
    """Pula automaticamente testes marcados como 'integration' quando o
    back-end nao esta disponivel."""
    if request.node.get_closest_marker("integration") and not api_available:
        pytest.skip(
            f"Back-end do FrioVale nao esta rodando em {DEFAULT_API_BASE}. "
            "Inicie o Spring Boot para executar testes de integracao."
        )


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """URL base da API do FrioVale.

    Pode ser sobrescrita pela variavel de ambiente FRIOVALE_API_URL.
    """
    return os.getenv("FRIOVALE_API_URL", DEFAULT_API_BASE)


@pytest.fixture
def api_headers() -> dict[str, str]:
    """Cabecalho padrao JSON para requisicoes."""
    return {"Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Dados de exemplo (fixtures de dominio)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_fruit() -> dict[str, Any]:
    """Fruta de exemplo com faixa de temperatura segura."""
    return {
        "id": 1,
        "name": "Manga",
        "minTemp": 10.0,
        "maxTemp": 13.0,
        "minHumidity": 85.0,
        "maxHumidity": 95.0,
    }


@pytest.fixture
def sample_trip() -> dict[str, Any]:
    """Viagem de exemplo."""
    return {
        "id": 101,
        "containerId": 7,
        "containerCode": "CONT-007",
        "driverId": 42,
        "driverName": "Joao Silva",
        "fruitId": 1,
        "fruitName": "Manga",
        "minTemp": 10.0,
        "maxTemp": 13.0,
        "minHumidity": 85.0,
        "maxHumidity": 95.0,
        "origin": "Petrolina (PE)",
        "destination": "Sao Paulo (SP)",
        "status": "IN_TRANSIT",
        "startDate": "2026-11-01T08:00:00",
        "endDate": None,
        "temperature": 11.5,
        "humidity": 90.0,
        "latitude": -9.3915,
        "longitude": -40.5131,
        "lastReadingAt": "2026-11-01T14:30:00",
        "inRange": True,
        "readings": 120,
        "readingsInRange": 118,
        "inRangePercent": 98.3,
    }


@pytest.fixture
def sample_telemetry_reading() -> dict[str, Any]:
    """Leitura de telemetria (ThingSpeak) de exemplo."""
    return {
        "entryId": 5550,
        "temperature": 11.8,
        "humidity": 89.0,
        "latitude": -9.3915,
        "longitude": -40.5131,
        "timestamp": "2026-11-01T14:30:00",
    }


@pytest.fixture
def sample_alert() -> dict[str, Any]:
    """Alerta de exemplo."""
    return {
        "id": 9,
        "tripId": 101,
        "containerCode": "CONT-007",
        "fruitName": "Manga",
        "telemetryId": 5550,
        "temperature": 14.2,
        "minTemp": 10.0,
        "maxTemp": 13.0,
        "telemetryTimestamp": "2026-11-01T15:00:00",
        "message": "Temperatura acima da faixa segura: 14.2°C (Manga: 10.0°C a 13.0°C) no contêiner CONT-007",
        "resolved": False,
        "createdAt": "2026-11-01T15:00:00",
    }


@pytest.fixture
def sample_user_driver() -> dict[str, Any]:
    """Usuario motorista de exemplo."""
    return {
        "id": 42,
        "name": "Joao Silva",
        "email": "joao@transportadora.com.br",
        "phone": "(87) 99999-0000",
        "role": "ROLE_DRIVER",
    }


@pytest.fixture
def sample_user_company() -> dict[str, Any]:
    """Usuario empresa (administrador) de exemplo."""
    return {
        "id": 1,
        "name": "Administrador FrioVale",
        "email": "admin@friovale.com.br",
        "phone": None,
        "role": "ROLE_COMPANY",
    }


@pytest.fixture
def sample_dashboard_summary() -> dict[str, Any]:
    """Resumo do dashboard de exemplo."""
    return {
        "activeTrips": 3,
        "tripsInRange": 2,
        "idealMinTemp": 10.0,
        "idealMaxTemp": 13.0,
        "activeAlerts": 1,
        "activeDrivers": 3,
        "trips": [],
        "recentAlerts": [],
    }


# ---------------------------------------------------------------------------
# Helpers de montagem de payloads
# ---------------------------------------------------------------------------

@pytest.fixture
def login_payload() -> dict[str, str]:
    """Payload de login com credenciais que podem não existir no banco.

    Mantido propositalmente para evidenciar um defeito: tentativa de login
    com usuário não cadastrado retorna 401 Unauthorized.
    """
    return {"email": "admin@friovale.com.br", "password": "senha123"}


@pytest.fixture
def admin_login_payload() -> dict[str, str]:
    """Payload de login do administrador bootstrap do FrioVale.

    Credenciais carregadas via propriedades de bootstrap:
      friovale.bootstrap.admin-email=gestor@friovale.com
      friovale.bootstrap.admin-password=TroqueEstaSenha123
    """
    return {"email": "gestor@friovale.com", "password": "TroqueEstaSenha123"}


@pytest.fixture
def register_payload() -> dict[str, str]:
    """Payload de cadastro."""
    return {
        "name": "Maria Oliveira",
        "email": "maria@transportadora.com.br",
        "phone": "(87) 98888-7777",
        "password": "senha123",
    }


@pytest.fixture
def trip_request_payload(sample_fruit) -> dict[str, Any]:
    """Payload de criacao de viagem."""
    return {
        "containerId": sample_fruit["id"],
        "driverId": 42,
        "fruitId": sample_fruit["id"],
        "origin": "Petrolina (PE)",
        "destination": "Sao Paulo (SP)",
        "shouldStartNow": True,
    }
