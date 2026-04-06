"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt leonanluppi/bug_to_user_story_v1
3. Salva localmente em prompts/raw_prompts.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_TO_PULL = "leonanluppi/bug_to_user_story_v1"
OUTPUT_FILE = "prompts/raw_prompts.yml"


def pull_prompts_from_langsmith() -> dict | None:
    """
    Faz pull do prompt do LangSmith Hub.

    Returns:
        Dicionário com dados do prompt ou None se erro
    """
    try:
        print(f"Fazendo pull do prompt: {PROMPT_TO_PULL}")

        prompt = hub.pull(PROMPT_TO_PULL)

        messages = prompt.messages
        system_prompt = ""
        user_prompt = ""

        for msg in messages:
            if msg.__class__.__name__ == "SystemMessagePromptTemplate":
                system_prompt = msg.prompt.template
            elif msg.__class__.__name__ == "HumanMessagePromptTemplate":
                user_prompt = msg.prompt.template

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }

        print(f"Prompt extraído com sucesso!")
        return prompt_data

    except Exception as e:
        print(f"Erro ao fazer pull do prompt: {e}")
        return None


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ['LANGSMITH_API_KEY']
    if not check_env_vars(required_vars):
        return 1

    prompt_data = pull_prompts_from_langsmith()
    if not prompt_data:
        return 1

    print(f"\nSalvando em: {OUTPUT_FILE}")
    if save_yaml(prompt_data, OUTPUT_FILE):
        print(f"Prompt salvo com sucesso!")

        print("\n--- Conteúdo do System Prompt ---")
        system = prompt_data["bug_to_user_story_v1"]["system_prompt"]
        print(system[:500] + "..." if len(system) > 500 else system)

        return 0
    else:
        print("Erro ao salvar arquivo.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
