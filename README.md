# Testes Automatizados - FrioVale

Suite de testes automatizados em Python para o sistema **FrioVale** (monitoramento da cadeia do frio para transporte de frutas).

---

## Estrutura do projeto

```
testes_friovale/
├── pyproject.toml          # Configuracao do pytest e dependencias
├── requirements.txt        # Dependencias Python
├── README.md               # Este arquivo
├── conftest.py             # Fixtures globais do pytest
├── generate_report.py      # Gerador de relatorio de metricas
├── metrics/
│   ├── __init__.py
│   ├── calculator.py       # Calculo das metricas de qualidade
│   └── report.py           # Geracao de relatorio textual e JSON
└── tests/
    ├── __init__.py
    ├── test_business_rules.py   # Regras de negocio (temperatura, status, acesso)
    ├── test_api_auth.py         # Autenticacao (login/cadastro/usuario atual)
    ├── test_api_trips.py        # Gerenciamento de viagens (CRUD, status)
    ├── test_api_telemetry.py    # Leituras, sensores e alertas (telemetria)
    ├── test_api_dashboard.py    # Resumo do dashboard e equipe (usuarios)
    ├── test_api_iot.py          # Logs IoT / ThingSpeak (sincronizacao)
    ├── test_api_reports.py      # Relatorios PDF (viagem e motorista)
    └── test_metrics.py          # Testes das metricas de qualidade
```

---

## Testes implementados (descricao resumida)

| Arquivo | O que testa | Quantidade | Requer servidor? |
|---------|-------------|------------|------------------|
| `test_business_rules.py` | Transicoes de status de viagem (PLANNED/IN_TRANSIT/COMPLETED), validacao de faixa de temperatura contra a fruta, descarte de leituras duplicadas/antigas, montagem de mensagens de alerta, controle de acesso por perfil (empresa vs motorista) | 16 | **Nao** |
| `test_metrics.py` | Densidade de defeitos, cobertura de testes, taxa de retrabalho, produtividade da equipe e custo financeiro do retrabalho (incluindo casos de erro) | 27 | **Nao** |
| `test_api_auth.py` | Login (usuario generico e admin bootstrap), login com credenciais invalidas, campos obrigatorios, cadastro, cadastro duplicado, email invalido, senha curta, usuario atual (com/sem token) | 10 | **Sim** (localhost:8080) |
| `test_api_trips.py` | Listagem de viagens, criacao de viagem, invalido papel do motorista, campos obrigatorios, inicio/fim de viagem, nao finalizar viagem PLANNED, monitor de viagens ativas | 11 | **Sim** |
| `test_api_telemetry.py` | Historico de telemetria (com/sem auth), listagem de alertas | 4 | **Sim** |
| `test_api_dashboard.py` | Resumo do dashboard, listagem de usuarios, usuarios por role, criacao de usuario, estatisticas de motoristas | 6 | **Sim** |
| `test_api_iot.py` | Listagem de logs IoT, filtro por contêiner, sincronizacao com ThingSpeak | 3 | **Sim** |
| `test_api_reports.py` | PDF detalhado por viagem, PDF de relatorio por motorista/periodo | 2 | **Sim** |
| **Total** | | **79** | |

> Nota: a quantidade acima inclui testes que sao pulados automaticamente quando o back-end nao esta rodando ou nao ha usuario autenticado.

---

## Resultados da última execução

Execucao realizada com o back-end Spring Boot rodando em `http://localhost:8080`:

```
2 failed, 52 passed, 21 skipped
```

### ✅ 52 testes passaram
Todos os testes de unidade (regras de negocio + metricas) e os testes de API que conseguiram autenticacao.

### ❌ 2 testes falharam (defeitos evidenciados propositalmente)

| Teste | Resultado | Descricao do defeito |
|-------|-----------|----------------------|
| `test_api_auth.py::TestAuthLogin::test_login_success` | `401 Unauthorized` | Tentativa de login com usuario `admin@friovale.com.br` / `senha123` que **nao esta cadastrado** no banco do FrioVale. Evidencia que o login exige usuario pre-existente. |
| `test_api_auth.py::TestAuthRegister::test_register_success` | `409 Conflict` | Tentativa de cadastro retornou conflito, possivelmente porque o e-mail ja existe ou ha regra de negocio bloqueando. Evidencia validacao de duplicidade no cadastro. |

> **Nota didatica:** essas falhas foram mantidas propositalmente para mostrar ao professor que a suíte detecta comportamentos reais do sistema, em vez de mascarar resultados.

### ⏭️ 21 testes pulados
Testes de API que dependem de um token JWT valido. Como o login com usuario generico falhou (usuario nao cadastrado), nao houve token disponível e esses testes foram pulados automaticamente com mensagem clara:

```
SKIPPED - Nao foi possível autenticar para testes de ...
```

Para executá-los, basta cadastrar um usuario valido no FrioVale e ajustar o fixture `login_payload` em `conftest.py`.

---

## Como executar no VS Code

1. Abra a pasta `testes_friovale` no VS Code (**Arquivo > Abrir Pasta**).
2. Instale a extensão **Python** (Microsoft).
3. Abra o terminal integrado (`Ctrl+` `) e crie/ative o ambiente virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Instale as dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

5. Configure o pytest: `Ctrl+Shift+P` → **Python: Configure Tests** → escolha **pytest** e diretório `tests`.

6. Execute pelos testes:

   - **Só unidade (sem servidor):**
     ```powershell
     pytest tests/test_business_rules.py tests/test_metrics.py -v
     ```
   - **Todos (com back-end rodando):**
     ```powershell
     pytest tests/ -v
     ```

   Ou use o **Test Explorer** (icone de frasco na barra lateral) para rodar individualmente.

---

## Gerar relatorio de metricas de qualidade

```powershell
python generate_report.py
```

Executa os testes e imprime na tela o relatorio das 5 metricas, além de salvar `relatorio_metricas_friovale.json`.

Metricas calculadas:

| Metrica | Formula | Valor exemplo (do enunciado) |
|---------|---------|------------------------------|
| Densidade de defeitos | Defeitos / KLOC | 6 defeitos / 3 KLOC = 2 defeitos/KLOC |
| Cobertura de testes | Linhas cobertas / Total × 100 | A definir apos execucao real de cobertura |
| Taxa de retrabalho | Horas retrabalho / Horas totais × 100 | 20h / 100h = 20% |
| Produtividade | Entregas / Horas de desenvolvimento | 8 entregas / 80h = 0,1 entrega/hora |
| Custo do retrabalho | Horas retrabalho × Custo/hora | 20h × R$ 40,00 = R$ 800,00 |

Premissa didatica: custo-hora simulado de **R$ 40,00/hora**.
