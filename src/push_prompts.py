"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get('system_prompt', '')
        user_prompt = prompt_data.get('user_prompt', '{bug_report}')

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        description = prompt_data.get('description', '')

        hub_name = f"{prompt_name}"

        print(f"Enviando prompt '{hub_name}' para o LangSmith Hub...")

        url = hub.push(
            hub_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=description
        )

        print(f"Prompt publicado com sucesso!")
        print(f"URL: {url}")
        return True

    except Exception as e:
        print(f"Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ['description', 'system_prompt', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA LANGSMITH HUB")

    required_vars = ['LANGSMITH_API_KEY']
    if not check_env_vars(required_vars):
        return 1

    prompts_file = "prompts/bug_to_user_story_v2.yml"
    print(f"INFO:Carregando prompts de: {prompts_file}")

    prompts_data = load_yaml(prompts_file)
    if not prompts_data:
        print("ERRO:Erro ao carregar arquivo de prompts.")
        return 1

    success_count = 0

    for prompt_name, prompt_data in prompts_data.items():
        print_section_header(f"Processando: {prompt_name}", char="-")

        is_valid, errors = validate_prompt(prompt_data)
        if not is_valid:
            print(f"ERRO:Prompt inválido:")
            for error in errors:
                print(f"  - {error}")
            continue

        print("INFO:Validação OK")

        if push_prompt_to_langsmith(prompt_name, prompt_data):
            success_count += 1

    print_section_header("RESUMO")
    print(f"SUCESSO:Prompts enviados com sucesso: {success_count}")

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
