from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
PROMPT_FILE = ROOT_DIR / "prompts" / "bug_to_user_story_v2.yml"


def load_prompt():
    with PROMPT_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def joined_prompt_text(prompt):
    return "\n".join([
        str(prompt.get("system_prompt", "")),
        str(prompt.get("user_prompt", "")),
    ])


def test_prompt_has_system_prompt():
    prompt = load_prompt()
    assert prompt.get("system_prompt")
    assert prompt["system_prompt"].strip()


def test_prompt_has_role_definition():
    text = joined_prompt_text(load_prompt()).lower()
    role_markers = ["você é", "product manager", "persona", "especializado"]
    assert any(marker in text for marker in role_markers)


def test_prompt_mentions_format():
    text = joined_prompt_text(load_prompt()).lower()
    assert "markdown" in text
    assert "como [persona], quero [objetivo], para [benefício]" in text
    assert "given" in text and "when" in text and "then" in text


def test_prompt_has_few_shot_examples():
    text = joined_prompt_text(load_prompt()).lower()
    assert text.count("entrada:") >= 2
    assert text.count("saída:") >= 2
    assert "few-shot learning" in str(load_prompt().get("metadata", {})).lower()


def test_prompt_no_todos():
    text = joined_prompt_text(load_prompt()).lower()
    assert "[todo]" not in text
    assert "todo:" not in text


def test_minimum_techniques():
    prompt = load_prompt()
    techniques = prompt.get("metadata", {}).get("techniques", [])
    assert isinstance(techniques, list)
    assert len(techniques) >= 2
