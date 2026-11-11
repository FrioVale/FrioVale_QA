"""Geracao de relatorio das metricas de qualidade do FrioVale."""

from __future__ import annotations

import json
from datetime import datetime

from metrics.calculator import MetricsReport


def build_text_report(report: MetricsReport) -> str:
    """Construi um relatorio textual formatado das metricas."""
    lines = []
    lines.append("=" * 70)
    lines.append("RELATORIO DE METRICAS DE QUALIDADE - SISTEMA FRIOVALE")
    lines.append("Monitoramento da cadeia do frio para transporte de frutas")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Data geracao: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lines.append("")

    # Metrica 1
    lines.append("-" * 70)
    lines.append("METRICA 1 - Densidade de defeitos (Metrica de produto)")
    lines.append("-" * 70)
    dd = report.defect_density
    lines.append(f"  Codigo analisado: {dd.kLOC * 1000:,.0f} LOC ({dd.kLOC:.3f} KLOC)")
    lines.append(f"  Defeitos registrados: {dd.defects}")
    lines.append(f"  Densidade: {dd.density:.2f} defeitos/KLOC")
    lines.append("  Observacao: funcionalidades ainda nao desenvolvidas nao contam como defeitos.")
    lines.append("")

    # Metrica 2
    lines.append("-" * 70)
    lines.append("METRICA 2 - Cobertura de testes automatizados (Metrica de produto)")
    lines.append("-" * 70)
    cov = report.coverage
    lines.append(f"  Linhas cobertas: {cov.covered_lines:,}")
    lines.append(f"  Total de linhas: {cov.total_lines:,}")
    lines.append(f"  Cobertura: {cov.percentage:.2f}%")
    lines.append(f"  Interpretacao: {cov.interpretation}")
    lines.append("")

    # Metrica 3
    lines.append("-" * 70)
    lines.append("METRICA 3 - Taxa de retrabalho (Metrica de processo)")
    lines.append("-" * 70)
    rw = report.rework_rate
    lines.append(f"  Horas de retrabalho: {rw.rework_hours} h")
    lines.append(f"  Horas totais trabalhadas: {rw.total_hours} h")
    lines.append(f"  Taxa de retrabalho: {rw.rate:.2f}%")
    lines.append("  Observacao: melhorias ou novas funcionalidades nao sao retrabalho.")
    lines.append("")

    # Metrica 4
    lines.append("-" * 70)
    lines.append("METRICA 4 - Produtividade da equipe (Metrica de processo)")
    lines.append("-" * 70)
    prod = report.productivity
    lines.append(f"  Entregas funcionais concluidas: {prod.deliveries}")
    lines.append(f"  Horas de desenvolvimento: {prod.dev_hours} h")
    lines.append(f"  Produtividade: {prod.productivity:.4f} entrega/hora")
    lines.append("")

    # Exigencia adicional
    lines.append("-" * 70)
    lines.append("EXIGENCIA ADICIONAL - Custo financeiro do retrabalho")
    lines.append("-" * 70)
    cost = report.rework_cost
    lines.append(f"  Horas de retrabalho: {cost.rework_hours} h")
    lines.append(f"  Custo-hora (premissa didatica): R$ {cost.cost_per_hour:.2f}")
    lines.append(f"  Custo total do retrabalho: R$ {cost.total_cost:,.2f}")
    lines.append("")
    lines.append("  Impactos de problemas tecnicos no negocio:")
    lines.append("    - Perda de confiança de transportadoras e exportadoras.")
    lines.append("    - Risco de falhas no monitoramento da cadeia do frio.")
    lines.append("    - Maior esforço de manutenção do software.")
    lines.append("    - Atrasos na implementacao de novas funcionalidades.")
    lines.append("    - Aumento dos custos de desenvolvimento.")
    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def build_json_report(report: MetricsReport) -> dict:
    """Construi o relatorio em formato dicionario (serializavel a JSON)."""
    return {
        "sistema": "FrioVale - Monitoramento da cadeia do frio",
        "data_geracao": datetime.now().isoformat(),
        "metricas": report.to_dict(),
    }


def save_json_report(report: MetricsReport, path: str = "relatorio_metricas_friovale.json") -> None:
    """Salva o relatorio em um arquivo JSON."""
    data = build_json_report(report)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_report(report: MetricsReport) -> None:
    """Imprime o relatorio textual no console."""
    print(build_text_report(report))
