"""Testes das metricas de qualidade de software do FrioVale.

Cobre as quatro metricas do professor mais a exigencia adicional
de custo financeiro do retrabalho.
"""

from __future__ import annotations

import pytest

from metrics.calculator import (
    calculate_coverage,
    calculate_defect_density,
    calculate_productivity,
    calculate_rework_cost,
    calculate_rework_rate,
)


# ---------------------------------------------------------------------------
# Metrica 1 - Densidade de defeitos
# ---------------------------------------------------------------------------


class TestDefectDensity:
    """Densidade = Defeitos / KLOC, onde KLOC = LOC / 1000."""

    def test_hypothetical_example_from_spec(self):
        """Exemplo do enunciado: 3.000 LOC, 6 defeitos -> 2 defeitos/KLOC."""
        result = calculate_defect_density(lines_of_code=3000, defects=6)
        assert result.kLOC == 3.0
        assert result.defects == 6
        assert result.density == 2.0

    def test_zero_loc_returns_zero_density(self):
        result = calculate_defect_density(lines_of_code=0, defects=0)
        assert result.kLOC == 0.0
        assert result.density == 0.0

    def test_single_defect_density(self):
        result = calculate_defect_density(lines_of_code=1500, defects=3)
        assert result.kLOC == 1.5
        assert result.density == 2.0

    def test_negative_loc_raises(self):
        with pytest.raises(ValueError):
            calculate_defect_density(lines_of_code=-100, defects=1)

    def test_negative_defects_raises(self):
        with pytest.raises(ValueError):
            calculate_defect_density(lines_of_code=1000, defects=-1)


# ---------------------------------------------------------------------------
# Metrica 2 - Cobertura de testes automatizados
# ---------------------------------------------------------------------------


class TestCoverage:
    """Cobertura = Linhas cobertas / Total de linhas x 100."""

    def test_hypothetical_example_from_spec(self):
        """400 linhas cobertas de 1.000 = 40% (abaixo de 70% -> atencao)."""
        result = calculate_coverage(covered_lines=400, total_lines=1000)
        assert result.percentage == 40.0
        assert result.interpretation.startswith("Abaixo de 70%")

    def test_good_coverage_above_80(self):
        result = calculate_coverage(covered_lines=850, total_lines=1000)
        assert result.percentage == 85.0
        assert result.interpretation.startswith("Acima de 80%")

    def test_intermediate_coverage_70_to_80(self):
        result = calculate_coverage(covered_lines=750, total_lines=1000)
        assert result.percentage == 75.0
        assert result.interpretation.startswith("70% a 80%")

    def test_boundary_70_percent_is_intermediate(self):
        result = calculate_coverage(covered_lines=700, total_lines=1000)
        assert result.percentage == 70.0
        assert result.interpretation.startswith("70% a 80%")

    def test_boundary_80_percent_is_intermediate(self):
        result = calculate_coverage(covered_lines=800, total_lines=1000)
        assert result.percentage == 80.0
        assert result.interpretation.startswith("70% a 80%")

    def test_zero_lines_returns_zero(self):
        result = calculate_coverage(covered_lines=0, total_lines=0)
        assert result.percentage == 0.0

    def test_covered_greater_than_total_raises(self):
        with pytest.raises(ValueError):
            calculate_coverage(covered_lines=1100, total_lines=1000)

    def test_negative_values_raise(self):
        with pytest.raises(ValueError):
            calculate_coverage(covered_lines=-10, total_lines=100)
        with pytest.raises(ValueError):
            calculate_coverage(covered_lines=10, total_lines=-100)


# ---------------------------------------------------------------------------
# Metrica 3 - Taxa de retrabalho
# ---------------------------------------------------------------------------


class TestReworkRate:
    """Taxa = Horas de retrabalho / Horas totais x 100."""

    def test_hypothetical_example_from_spec(self):
        """20h retrabalho / 100h total = 20%."""
        result = calculate_rework_rate(rework_hours=20, total_hours=100)
        assert result.rework_hours == 20
        assert result.total_hours == 100
        assert result.rate == 20.0

    def test_no_rework_is_zero_percent(self):
        result = calculate_rework_rate(rework_hours=0, total_hours=100)
        assert result.rate == 0.0

    def test_all_hours_rework_is_100_percent(self):
        result = calculate_rework_rate(rework_hours=80, total_hours=80)
        assert result.rate == 100.0

    def test_zero_total_hours_raises(self):
        with pytest.raises(ValueError):
            calculate_rework_rate(rework_hours=10, total_hours=0)

    def test_negative_values_raise(self):
        with pytest.raises(ValueError):
            calculate_rework_rate(rework_hours=-5, total_hours=100)
        with pytest.raises(ValueError):
            calculate_rework_rate(rework_hours=150, total_hours=100)


# ---------------------------------------------------------------------------
# Metrica 4 - Produtividade da equipe
# ---------------------------------------------------------------------------


class TestProductivity:
    """Produtividade = Entregas concluidas / Horas de desenvolvimento."""

    def test_hypothetical_example_from_spec(self):
        """8 entregas / 80h dev = 0.1 entrega por hora."""
        result = calculate_productivity(deliveries=8, dev_hours=80)
        assert result.deliveries == 8
        assert result.dev_hours == 80
        assert result.productivity == 0.1

    def test_zero_deliveries_is_zero_productivity(self):
        result = calculate_productivity(deliveries=0, dev_hours=80)
        assert result.productivity == 0.0

    def test_zero_dev_hours_raises(self):
        with pytest.raises(ValueError):
            calculate_productivity(deliveries=5, dev_hours=0)

    def test_negative_deliveries_raises(self):
        with pytest.raises(ValueError):
            calculate_productivity(deliveries=-1, dev_hours=80)


# ---------------------------------------------------------------------------
# Exigencia adicional - Custo financeiro do retrabalho
# ---------------------------------------------------------------------------


class TestReworkCost:
    """Custo = Horas de retrabalho x Custo/hora (premissa: R$ 40,00/h)."""

    def test_hypothetical_example_from_spec(self):
        """20h x R$ 40,00 = R$ 800,00."""
        result = calculate_rework_cost(rework_hours=20, cost_per_hour=40.0)
        assert result.rework_hours == 20
        assert result.cost_per_hour == 40.0
        assert result.total_cost == 800.0

    def test_default_cost_per_hour_is_40(self):
        """Premissa didatica do FrioVale: custo-hora simulado de R$ 40,00."""
        result = calculate_rework_cost(rework_hours=10)
        assert result.cost_per_hour == 40.0
        assert result.total_cost == 400.0

    def test_zero_rework_hours_is_zero_cost(self):
        result = calculate_rework_cost(rework_hours=0, cost_per_hour=40.0)
        assert result.total_cost == 0.0

    def test_negative_values_raise(self):
        with pytest.raises(ValueError):
            calculate_rework_cost(rework_hours=-5, cost_per_hour=40.0)
        with pytest.raises(ValueError):
            calculate_rework_cost(rework_hours=10, cost_per_hour=-10.0)
