from __future__ import annotations

from langchain import hub

from utils import PROMPTS_DIR, chat_template_to_yaml, load_environment, write_yaml

SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_FILE = PROMPTS_DIR / "bug_to_user_story_v1.yml"


def pull_prompt() -> None:
    load_environment()
    print(f"Fazendo pull do prompt {SOURCE_PROMPT}...")
    prompt = hub.pull(SOURCE_PROMPT)
    prompt_data = chat_template_to_yaml("bug_to_user_story_v1", prompt)
    prompt_data["langsmith_source"] = SOURCE_PROMPT
    write_yaml(OUTPUT_FILE, prompt_data)
    print(f"Prompt salvo em {OUTPUT_FILE}")


if __name__ == "__main__":
    pull_prompt()
