"""Calculo das metricas de qualidade de software do FrioVale.

Implementa as quatro metricas solicitadas pelo professor mais a
exigencia adicional de custo financeiro do retrabalho.

Metrica 1 - Densidade de defeitos (produto)
Metrica 2 - Cobertura de testes automatizados (produto)
Metrica 3 - Taxa de retrabalho (processo)
Metrica 4 - Produtividade da equipe (processo)
Adicional   - Custo financeiro do retrabalho
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Metrica 1 - Densidade de defeitos
# ---------------------------------------------------------------------------

@dataclass
class DefectDensityResult:
    kLOC: float
    defects: int
    density: float  # defeitos por KLOC


def calculate_defect_density(lines_of_code: int, defects: int) -> DefectDensityResult:
    """Calcula a densidade de defeitos.

    Formula:
        KLOC  = LOC / 1000
        Densidade = Defeitos / KLOC

    Atencao: funcionalidades ainda nao desenvolvidas nao contam como defeitos.
    """
    if lines_of_code < 0:
        raise ValueError("LOC nao pode ser negativo.")
    if defects < 0:
        raise ValueError("Quantidade de defeitos nao pode ser negativa.")

    kloc = lines_of_code / 1000.0
    density = defects / kloc if kloc > 0 else 0.0
    return DefectDensityResult(kLOC=kloc, defects=defects, density=density)


# ---------------------------------------------------------------------------
# Metrica 2 - Cobertura de testes automatizados
# ---------------------------------------------------------------------------

@dataclass
class CoverageResult:
    covered_lines: int
    total_lines: int
    percentage: float
    interpretation: str


def calculate_coverage(covered_lines: int, total_lines: int) -> CoverageResult:
    """Calcula a cobertura de testes automatizados.

    Formula:
        Cobertura = (Linhas cobertas / Total de linhas) x 100

    Interpretacao didatica:
        < 70%  : Atencao
        70-80% : Faixa intermediaria
        > 80%  : Boa cobertura
    """
    if total_lines < 0:
        raise ValueError("Total de linhas nao pode ser negativo.")
    if covered_lines < 0:
        raise ValueError("Linhas cobertas nao pode ser negativo.")
    if covered_lines > total_lines:
        raise ValueError("Linhas cobertas nao podem exceder o total de linhas.")

    percentage = (covered_lines / total_lines * 100.0) if total_lines > 0 else 0.0

    if percentage < 70.0:
        interpretation = "Abaixo de 70% - Atencao"
    elif percentage <= 80.0:
        interpretation = "70% a 80% - Faixa intermediaria"
    else:
        interpretation = "Acima de 80% - Boa cobertura"

    return CoverageResult(
        covered_lines=covered_lines,
        total_lines=total_lines,
        percentage=percentage,
        interpretation=interpretation,
    )


# ---------------------------------------------------------------------------
# Metrica 3 - Taxa de retrabalho
# ---------------------------------------------------------------------------

@dataclass
class ReworkRateResult:
    rework_hours: float
    total_hours: float
    rate: float  # percentual


def calculate_rework_rate(rework_hours: float, total_hours: float) -> ReworkRateResult:
    """Calcula a taxa de retrabalho.

    Formula:
        Taxa = (Horas de retrabalho / Horas totais) x 100

    Melhorias ou novas funcionalidades nao sao classificadas como retrabalho.
    """
    if total_hours <= 0:
        raise ValueError("Horas totais devem ser maiores que zero.")
    if rework_hours < 0:
        raise ValueError("Horas de retrabalho nao podem ser negativas.")
    if rework_hours > total_hours:
        raise ValueError("Horas de retrabalho nao podem exceder as horas totais.")

    rate = rework_hours / total_hours * 100.0
    return ReworkRateResult(
        rework_hours=rework_hours,
        total_hours=total_hours,
        rate=rate,
    )


# ---------------------------------------------------------------------------
# Metrica 4 - Produtividade da equipe
# ---------------------------------------------------------------------------

@dataclass
class ProductivityResult:
    deliveries: int
    dev_hours: float
    productivity: float  # entregas por hora


def calculate_productivity(deliveries: int, dev_hours: float) -> ProductivityResult:
    """Calcula a produtividade da equipe (abordagem A - entregas por hora).

    Formula:
        Produtividade = Entregas concluidas / Horas de desenvolvimento
    """
    if dev_hours <= 0:
        raise ValueError("Horas de desenvolvimento devem ser maiores que zero.")
    if deliveries < 0:
        raise ValueError("Quantidade de entregas nao pode ser negativa.")

    productivity = deliveries / dev_hours
    return ProductivityResult(
        deliveries=deliveries,
        dev_hours=dev_hours,
        productivity=productivity,
    )


# ---------------------------------------------------------------------------
# Exigencia adicional - Custo financeiro do retrabalho
# ---------------------------------------------------------------------------

@dataclass
class ReworkCostResult:
    rework_hours: float
    cost_per_hour: float
    total_cost: float


def calculate_rework_cost(rework_hours: float, cost_per_hour: float = 40.0) -> ReworkCostResult:
    """Calcula o custo financeiro do retrabalho.

    Formula:
        Custo = Horas de retrabalho x Custo/hora

    Premissa didatica para o FrioVale: custo-hora simulado de R$ 40,00,
    a ser explicitamente identificado como premissa na apresentacao.
    """
    if rework_hours < 0:
        raise ValueError("Horas de retrabalho nao podem ser negativas.")
    if cost_per_hour < 0:
        raise ValueError("Custo por hora nao pode ser negativo.")

    total_cost = rework_hours * cost_per_hour
    return ReworkCostResult(
        rework_hours=rework_hours,
        cost_per_hour=cost_per_hour,
        total_cost=total_cost,
    )


# ---------------------------------------------------------------------------
# Resultado consolidado de todas as metricas
# ---------------------------------------------------------------------------

@dataclass
class MetricsReport:
    defect_density: DefectDensityResult
    coverage: CoverageResult
    rework_rate: ReworkRateResult
    productivity: ProductivityResult
    rework_cost: ReworkCostResult

    def to_dict(self) -> dict:
        return {
            "defect_density": {
                "kloc": self.defect_density.kLOC,
                "defects": self.defect_density.defects,
                "density_per_kloc": self.defect_density.density,
            },
            "coverage": {
                "covered_lines": self.coverage.covered_lines,
                "total_lines": self.coverage.total_lines,
                "percentage": self.coverage.percentage,
                "interpretation": self.coverage.interpretation,
            },
            "rework_rate": {
                "rework_hours": self.rework_rate.rework_hours,
                "total_hours": self.rework_rate.total_hours,
                "rate_percent": self.rework_rate.rate,
            },
            "productivity": {
                "deliveries": self.productivity.deliveries,
                "dev_hours": self.productivity.dev_hours,
                "productivity_per_hour": self.productivity.productivity,
            },
            "rework_cost": {
                "rework_hours": self.rework_cost.rework_hours,
                "cost_per_hour": self.rework_cost.cost_per_hour,
                "total_cost": self.rework_cost.total_cost,
            },
        }
