# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Este repositório implementa o desafio de pull, otimização, push e avaliação de prompts do LangSmith Prompt Hub. O caso trabalhado converte bug reports em user stories claras, testáveis e úteis para backlog.

## Técnicas Aplicadas (Fase 2)

### Few-shot Learning

Usei exemplos completos de entrada e saída dentro do `user_prompt`. Os exemplos mostram como transformar bugs de checkout e pedidos em user stories com contexto, critérios de aceite, severidade, prioridade, dúvidas e notas para QA/Engenharia.

Motivo: exemplos reduzem ambiguidade, melhoram aderência ao formato esperado e aumentam F1/Correctness porque o modelo passa a copiar a estrutura e o nível de detalhe esperado.

### Skeleton of Thought

O prompt exige uma estrutura fixa em Markdown:

- `# User Story`
- `## Contexto do Bug`
- `## Critérios de Aceite`
- `## Severidade e Prioridade`
- `## Perguntas em aberto`
- `## Notas para QA/Engenharia`

Motivo: a estrutura melhora clareza, facilita avaliação automatizada e torna a saída mais útil para times de Produto, Engenharia e QA.

### Role Prompting

O `system_prompt` define a persona: Product Manager sênior especializado em triagem de bugs, user stories e alinhamento entre Produto, Engenharia, QA e Suporte.

Motivo: a persona orienta decisões de priorização, severidade, impacto e escrita voltada a backlog.

### Tratamento de edge cases

O prompt instrui o modelo a não inventar fatos, explicitar lacunas em `Perguntas em aberto`, mascarar dados sensíveis e lidar com bugs ambíguos criando uma história mínima.

Motivo: bugs reais costumam ter dados incompletos. Esse tratamento aumenta precisão e reduz alucinação.

## Resultados Finais

Resultado esperado após iterações no LangSmith: todas as métricas acima de `0.8`.

| Métrica | v1 ruim esperado | v2 otimizado esperado |
|---|---:|---:|
| Helpfulness | 0.45 | >= 0.80 |
| Correctness | 0.52 | >= 0.80 |
| F1-Score | 0.48 | >= 0.80 |
| Clarity | 0.50 | >= 0.80 |
| Precision | 0.46 | >= 0.80 |

Link público do dashboard LangSmith: preencha após executar `src/push_prompts.py` e publicar as avaliações.

Screenshots das avaliações: adicione nesta seção após capturar as execuções com notas mínimas atingidas.

## Como Executar

### 1. Criar e ativar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

- `LANGSMITH_API_KEY`
- `LANGSMITH_USERNAME`
- `OPENAI_API_KEY` ou `GOOGLE_API_KEY`
- `LLM_PROVIDER=openai` ou `LLM_PROVIDER=gemini`

### 3. Fazer pull do prompt v1

```bash
python src/pull_prompts.py
```

O script puxa `leonanluppi/bug_to_user_story_v1` e salva em `prompts/bug_to_user_story_v1.yml`.

### 4. Validar o prompt otimizado

```bash
pytest tests/test_prompts.py
```

### 5. Fazer push do prompt v2

```bash
python src/push_prompts.py
```

O script publica o prompt como `{LANGSMITH_USERNAME}/bug_to_user_story_v2`, adiciona descrição, tags e tenta marcá-lo como público.

### 6. Executar avaliação

```bash
python src/evaluate.py
```

A avaliação local imprime as cinco métricas exigidas. Para a entrega final, execute também a avaliação rastreada no LangSmith e registre o link público ou screenshots nesta documentação.

## Estrutura

```text
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
├── prompts/
│   ├── bug_to_user_story_v1.yml
│   └── bug_to_user_story_v2.yml
├── datasets/
│   └── bug_to_user_story.jsonl
├── src/
│   ├── pull_prompts.py
│   ├── push_prompts.py
│   ├── evaluate.py
│   ├── metrics.py
│   └── utils.py
└── tests/
    └── test_prompts.py
```

## Iteração Recomendada

1. Execute `python src/evaluate.py`.
2. Identifique a menor métrica.
3. Ajuste `prompts/bug_to_user_story_v2.yml`.
4. Faça push com `python src/push_prompts.py`.
5. Reavalie no LangSmith.
6. Repita até todas as métricas ficarem `>= 0.8`.
