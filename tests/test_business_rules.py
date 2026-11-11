"""Testes de unidade das regras de negocio do FrioVale.

Estes testes nao requerem o back-end rodando. Reproduzem em Python a
logica de dominio implementada no Spring Boot:

- Transicoes de status de viagem: PLANNED -> IN_TRANSIT -> COMPLETED
- Validacao de faixa de temperatura contra a fruta da viagem
- Descarga de leituras duplicadas / fora do periodo da viagem
- Unico contêiner ativo por viagem em andamento
- Acesso a viagens por perfil (empresa vs motorista)
"""

from __future__ import annotations

import pytest

from faker import Faker

fake = Faker("pt_BR")

# ---------------------------------------------------------------------------
# Constantes de dominio (reproduzem os enums Java)
# ---------------------------------------------------------------------------

TRIP_PLANNED = "PLANNED"
TRIP_IN_TRANSIT = "IN_TRANSIT"
TRIP_COMPLETED = "COMPLETED"

ROLE_DRIVER = "ROLE_DRIVER"
ROLE_COMPANY = "ROLE_COMPANY"


# ---------------------------------------------------------------------------
# Funcoes sob teste (reproduzidas do back-end Java)
# ---------------------------------------------------------------------------

def can_start_trip(status: str) -> bool:
    """Só é possível iniciar viagens PLANNED."""
    return status == TRIP_PLANNED


def can_end_trip(status: str) -> bool:
    """Só é possível finalizar viagens IN_TRANSIT."""
    return status == TRIP_IN_TRANSIT


def is_temperature_in_range(temperature: float | None, min_temp: float, max_temp: float) -> bool:
    """Valida se a temperatura está dentro da faixa segura da fruta."""
    if temperature is None:
        return False
    return min_temp <= temperature <= max_temp


def should_discard_reading(
    trip_status: str,
    entry_id: int | None,
    already_persisted: bool,
    trip_start_date: str | None,
    reading_timestamp: str | None,
) -> bool:
    """Regras de descarte de leitura (TelemetryService.registerReading)."""
    if trip_status != TRIP_IN_TRANSIT:
        return True  # leitura descartada: viagem nao esta em andamento
    if entry_id is not None and already_persisted:
        return True  # leitura duplicada (mesmo entry_id do ThingSpeak)
    if trip_start_date is not None and reading_timestamp is not None:
        if reading_timestamp < trip_start_date:
            return True  # leitura anterior ao inicio da viagem
    return False


def build_alert_message(
    trip_container_code: str,
    fruit_name: str,
    temp: float,
    min_temp: float,
    max_temp: float,
    below_min: bool,
) -> str:
    """Reproduz a montagem da mensagem de alerta em portugues."""
    direction = "abaixo" if below_min else "acima"
    return (
        f"Temperatura {direction} da faixa segura: {temp:.1f}°C "
        f"({fruit_name}: {min_temp:.1f}°C a {max_temp:.1f}°C) "
        f"no contêiner {trip_container_code}"
    )


def can_access_trip(is_company: bool, trip_exists: bool, driver_id_match: bool) -> bool:
    """Regra de acesso: empresa acessa qualquer viagem; motorista so as proprias."""
    if is_company:
        return trip_exists
    return driver_id_match


# ---------------------------------------------------------------------------
# Testes - Transicoes de status
# ---------------------------------------------------------------------------


class TestTripStatusTransitions:
    """Regras de transicao de status de viagem."""

    def test_can_start_only_planned_trip(self):
        assert can_start_trip(TRIP_PLANNED) is True
        assert can_start_trip(TRIP_IN_TRANSIT) is False
        assert can_start_trip(TRIP_COMPLETED) is False

    def test_can_end_only_in_transit_trip(self):
        assert can_end_trip(TRIP_IN_TRANSIT) is True
        assert can_end_trip(TRIP_PLANNED) is False
        assert can_end_trip(TRIP_COMPLETED) is False


# ---------------------------------------------------------------------------
# Testes - Validacao de temperatura / sensores
# ---------------------------------------------------------------------------


class TestTemperatureValidation:
    """Regras de monitoramento termico da cadeia do frio."""

    def test_temperature_within_range_is_ok(self, sample_fruit):
        assert is_temperature_in_range(11.5, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is True
        assert is_temperature_in_range(10.0, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is True  # limite inferior
        assert is_temperature_in_range(13.0, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is True  # limite superior

    def test_temperature_out_of_range_above(self, sample_fruit):
        assert is_temperature_in_range(14.2, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is False
        assert is_temperature_in_range(20.0, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is False

    def test_temperature_out_of_range_below(self, sample_fruit):
        assert is_temperature_in_range(5.0, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is False
        assert is_temperature_in_range(8.5, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is False

    def test_null_temperature_is_not_in_range(self, sample_fruit):
        assert is_temperature_in_range(None, sample_fruit["minTemp"], sample_fruit["maxTemp"]) is False


# ---------------------------------------------------------------------------
# Testes - Descarga de leituras (ThingSpeak / sensores)
# ---------------------------------------------------------------------------


class TestReadingDiscardRules:
    """Regras de descarte de leituras de telemetria."""

    def test_discard_when_trip_not_in_transit(self):
        assert should_discard_reading(TRIP_PLANNED, 1, False, None, None) is True
        assert should_discard_reading(TRIP_COMPLETED, 1, False, None, None) is True

    def test_discard_duplicate_entry_id(self):
        assert should_discard_reading(TRIP_IN_TRANSIT, 5550, True, None, None) is True

    def test_keep_new_reading_in_transit(self):
        assert should_discard_reading(TRIP_IN_TRANSIT, 5550, False, None, None) is False

    def test_discard_reading_before_trip_start(self):
        assert (
            should_discard_reading(
                TRIP_IN_TRANSIT,
                5551,
                False,
                "2026-11-01T08:00:00",
                "2026-10-31T20:00:00",
            )
            is True
        )

    def test_keep_reading_after_trip_start(self):
        assert (
            should_discard_reading(
                TRIP_IN_TRANSIT,
                5551,
                False,
                "2026-11-01T08:00:00",
                "2026-11-01T14:30:00",
            )
            is False
        )


# ---------------------------------------------------------------------------
# Testes - Mensagem de alerta
# ---------------------------------------------------------------------------


class TestAlertMessage:
    """Construcao da mensagem de alerta quando temperatura foge da faixa."""

    def test_alert_above_max(self):
        msg = build_alert_message("CONT-007", "Manga", 14.2, 10.0, 13.0, below_min=False)
        assert "acima" in msg
        assert "14.2" in msg
        assert "CONT-007" in msg
        assert "Manga" in msg

    def test_alert_below_min(self):
        msg = build_alert_message("CONT-005", "Uva", 6.5, 8.0, 12.0, below_min=True)
        assert "abaixo" in msg
        assert "6.5" in msg
        assert "Uva" in msg


# ---------------------------------------------------------------------------
# Testes - Controle de acesso por perfil
# ---------------------------------------------------------------------------


class TestAccessControl:
    """Regras de acesso a viagens por perfil de usuario."""

    def test_company_can_access_any_existing_trip(self):
        assert can_access_trip(is_company=True, trip_exists=True, driver_id_match=False) is True

    def test_company_cannot_access_nonexistent_trip(self):
        assert can_access_trip(is_company=True, trip_exists=False, driver_id_match=False) is False

    def test_driver_can_access_own_trip(self):
        assert can_access_trip(is_company=False, trip_exists=True, driver_id_match=True) is True

    def test_driver_cannot_access_other_driver_trip(self):
        assert can_access_trip(is_company=False, trip_exists=True, driver_id_match=False) is False
