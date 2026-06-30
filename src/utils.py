from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

ROOT_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT_DIR / "prompts"
DATASETS_DIR = ROOT_DIR / "datasets"


def load_environment() -> None:
    load_dotenv(ROOT_DIR / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente obrigatória ausente: {name}")
    return value


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"YAML inválido em {path}")
    return data


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)


def prompt_to_chat_template(prompt_data: Dict[str, Any]) -> ChatPromptTemplate:
    system_prompt = prompt_data.get("system_prompt") or ""
    user_prompt = prompt_data.get("user_prompt") or ""
    if not user_prompt.strip():
        raise ValueError("O campo user_prompt é obrigatório e não pode estar vazio.")
    messages = []
    if system_prompt.strip():
        messages.append(("system", system_prompt))
    messages.append(("user", user_prompt))
    return ChatPromptTemplate.from_messages(messages)


def chat_template_to_yaml(name: str, prompt: Any) -> Dict[str, Any]:
    messages = getattr(prompt, "messages", [])
    system_parts = []
    user_parts = []
    for message in messages:
        role = getattr(message, "role", None) or getattr(message, "_role", None)
        template = getattr(message, "prompt", None)
        text = getattr(template, "template", None) or getattr(message, "template", None) or str(message)
        if role == "system" or "SystemMessage" in type(message).__name__:
            system_parts.append(text)
        else:
            user_parts.append(text)
    return {
        "name": name,
        "description": "Prompt importado do LangSmith Prompt Hub.",
        "metadata": {"version": "v1", "status": "pulled"},
        "system_prompt": "\n".join(system_parts).strip(),
        "user_prompt": "\n".join(user_parts).strip(),
    }
