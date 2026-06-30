from __future__ import annotations

import os

from langchain import hub
from langsmith import Client

from utils import PROMPTS_DIR, load_environment, prompt_to_chat_template, read_yaml, require_env

PROMPT_FILE = PROMPTS_DIR / "bug_to_user_story_v2.yml"


def push_prompt() -> str:
    load_environment()
    username = require_env("LANGSMITH_USERNAME")
    prompt_data = read_yaml(PROMPT_FILE)
    prompt_name = f"{username}/bug_to_user_story_v2"
    prompt = prompt_to_chat_template(prompt_data)
    metadata = prompt_data.get("metadata", {})

    print(f"Fazendo push do prompt {prompt_name}...")
    url = hub.push(
        prompt_name,
        prompt,
        description=prompt_data.get("description", "Prompt otimizado para bug_to_user_story."),
        tags=metadata.get("tags", []),
    )

    client = Client(api_url=os.getenv("LANGSMITH_ENDPOINT") or None)
    try:
        client.update_prompt(prompt_name, is_public=True)
        print("Prompt marcado como público no LangSmith.")
    except Exception as exc:
        print(f"Aviso: não foi possível marcar como público automaticamente: {exc}")

    print(f"Prompt publicado: {url}")
    print(f"Técnicas registradas: {', '.join(metadata.get('techniques', []))}")
    return str(url)


if __name__ == "__main__":
    push_prompt()
