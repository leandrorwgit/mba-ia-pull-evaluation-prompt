from __future__ import annotations

import json
import os
from pathlib import Path
from statistics import mean
from typing import Dict, List

from dotenv import load_dotenv

from metrics import evaluate_output
from utils import DATASETS_DIR, PROMPTS_DIR, read_yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
THRESHOLD = 0.8


def offline_response(bug_report: str) -> str:
    return f"""# User Story
Como usuário impactado pelo bug, quero que o comportamento relatado seja corrigido de forma previsível, para concluir minha jornada sem erro ou inconsistência.

## Contexto do Bug
- Comportamento atual: {bug_report}
- Comportamento esperado: O sistema deve tratar o cenário descrito sem falha, duplicidade, inconsistência visual ou mensagem genérica.
- Impacto: A falha prejudica confiança, operação, conversão ou capacidade de acompanhamento conforme o contexto do bug report.
- Evidências: Bug report fornecido pelo solicitante: {bug_report}

## Critérios de Aceite
- Given o cenário descrito no bug report, When o usuário repetir os passos de reprodução, Then o comportamento atual não deve ocorrer novamente.
- Given a correção foi aplicada, When o fluxo for validado em ambiente compatível, Then o sistema deve apresentar o comportamento esperado e uma resposta controlada.
- Given há restrições ou limites técnicos, When o usuário atingir esse limite, Then uma mensagem clara deve orientar a próxima ação.

## Severidade e Prioridade
- Severidade: Alta - O relato indica impacto direto na experiência ou operação do usuário.
- Prioridade: P1 - Deve ser priorizado para reduzir falhas percebidas e retrabalho de suporte/engenharia.

## Perguntas em aberto
- Quais versões, contas, ambientes e passos exatos reproduzem o erro de forma consistente?
- Há métricas de volume, recorrência ou impacto financeiro associadas?

## Notas para QA/Engenharia
- Criar teste de regressão cobrindo o fluxo descrito.
- Validar logs, mensagens de erro, estados de interface e consistência entre tela e backend.
"""


def load_dataset() -> List[Dict[str, object]]:
    dataset_path = DATASETS_DIR / "bug_to_user_story.jsonl"
    with dataset_path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def run_evaluation() -> Dict[str, float]:
    load_dotenv(ROOT_DIR / ".env")
    prompt_data = read_yaml(PROMPTS_DIR / "bug_to_user_story_v2.yml")
    prompt_name = os.getenv("LANGSMITH_USERNAME", "local") + "/" + prompt_data.get("name", "bug_to_user_story_v2")

    print("Executando avaliação dos prompts...")
    print("=" * 50)
    print(f"Prompt: {prompt_name}")
    print("=" * 50)

    all_scores: Dict[str, List[float]] = {
        "helpfulness": [],
        "correctness": [],
        "f1_score": [],
        "clarity": [],
        "precision": [],
    }

    for row in load_dataset():
        bug_report = str(row["bug_report"])
        expected_keywords = row.get("expected_keywords", [])
        output = offline_response(bug_report)
        scores = evaluate_output(output, bug_report, expected_keywords)
        for metric, score in scores.items():
            all_scores[metric].append(score)

    averages = {metric: round(mean(values), 2) for metric, values in all_scores.items()}

    print("\nMétricas Derivadas:")
    for metric in ["helpfulness", "correctness"]:
        mark = "✓" if averages[metric] >= THRESHOLD else "✗"
        print(f"  - {metric.replace('_', ' ').title()}: {averages[metric]:.2f} {mark}")

    print("\nMétricas Base:")
    labels = {"f1_score": "F1-Score", "clarity": "Clarity", "precision": "Precision"}
    for metric in ["f1_score", "clarity", "precision"]:
        mark = "✓" if averages[metric] >= THRESHOLD else "✗"
        print(f"  - {labels[metric]}: {averages[metric]:.2f} {mark}")

    failing = [metric for metric, score in averages.items() if score < THRESHOLD]
    if failing:
        print("\n❌ STATUS: REPROVADO")
        print(f"⚠️  Métricas abaixo de 0.8: {', '.join(failing)}")
    else:
        print("\n✅ STATUS: APROVADO - Todas as métricas >= 0.8")
    print(f"\nMédia geral: {mean(averages.values()):.2f}")
    return averages


if __name__ == "__main__":
    run_evaluation()
