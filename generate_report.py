"""Ponto de entrada para executar os testes e gerar o relatorio de metricas.

Uso:
    python generate_report.py
"""

from __future__ import annotations

import subprocess
import sys

from metrics.calculator import (
    calculate_coverage,
    calculate_defect_density,
    calculate_productivity,
    calculate_rework_cost,
    calculate_rework_rate,
)
from metrics.report import print_report, save_json_report


def build_metrics_report():
    """Construi o relatorio de metricas com valores de referencia do FrioVale.

    Valores baseados no enunciado da disciplina:
      - Codigo: 3.000 LOC (3 KLOC), 6 defeitos -> densidade 2 defeitos/KLOC
      - Cobertura: linhas cobertas e total a serem preenchidas apos execucao
      - Retrabalho: 20 horas de 100 horas totais -> 20%
      - Produtividade: 8 entregas / 80 horas de desenvolvimento -> 0.1 entrega/h
      - Custo retrabalho: 20h x R$ 40,00 = R$ 800,00 (premissa didatica)
    """
    # --- Metrica 1: Densidade de defeitos ---
    loc = 3000
    defects = 6
    defect_density = calculate_defect_density(loc, defects)

    # --- Metrica 2: Cobertura de testes automatizados ---
    # A serem preenchidas apos rodar a cobertura real do projeto.
    covered_lines = 0
    total_lines = loc
    coverage = calculate_coverage(covered_lines, total_lines)

    # --- Metrica 3: Taxa de retrabalho ---
    rework_hours = 20.0
    total_hours = 100.0
    rework_rate = calculate_rework_rate(rework_hours, total_hours)

    # --- Metrica 4: Produtividade da equipe ---
    deliveries = 8
    dev_hours = 80.0
    productivity = calculate_productivity(deliveries, dev_hours)

    # --- Exigencia adicional: Custo financeiro do retrabalho ---
    cost_per_hour = 40.0  # premissa didatica simulada
    rework_cost = calculate_rework_cost(rework_hours, cost_per_hour)

    from metrics.calculator import MetricsReport

    return MetricsReport(
        defect_density=defect_density,
        coverage=coverage,
        rework_rate=rework_rate,
        productivity=productivity,
        rework_cost=rework_cost,
    )


def run_tests():
    """Executa a sueste de testes com pytest."""
    print(">>> Executando testes automatizados do FrioVale...\n")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=False,
    )
    return result.returncode


def main():
    exit_code = run_tests()

    print("\n" + "=" * 70)
    print(">>> Gerando relatorio de metricas de qualidade...")
    report = build_metrics_report()
    print_report(report)
    save_json_report(report, "relatorio_metricas_friovale.json")
    print("\nRelatorio salvo em: relatorio_metricas_friovale.json")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
