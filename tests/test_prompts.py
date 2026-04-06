"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        file_load = load_prompts('prompts/bug_to_user_story_v2.yml')
        file_load = file_load.get('bug_to_user_story_v2', {})
        assert 'system_prompt' in file_load
        assert file_load['system_prompt'] is not None and file_load['system_prompt'].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona."""
        file_load = load_prompts('prompts/bug_to_user_story_v2.yml')
        file_load = file_load.get('bug_to_user_story_v2', {})
        system_prompt = file_load.get('system_prompt', '')
        assert "você é um" in system_prompt.lower()

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        file_load = load_prompts('prompts/bug_to_user_story_v2.yml')
        file_load = file_load.get('bug_to_user_story_v2', {})
        system_prompt = file_load.get('system_prompt', '')
        assert "markdown" in system_prompt.lower() or "user story" in system_prompt.lower()

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        file_load = load_prompts('prompts/bug_to_user_story_v2.yml')
        file_load = file_load.get('bug_to_user_story_v2', {})
        system_prompt = file_load.get('system_prompt', '')
        assert "exemplo" in system_prompt.lower() or "example" in system_prompt.lower()

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        file_load = load_prompts('prompts/bug_to_user_story_v2.yml')
        file_load = file_load.get('bug_to_user_story_v2', {})
        system_prompt = file_load.get('system_prompt', '')
        user_prompt = file_load.get('user_prompt', '')
        assert "[TODO]" not in system_prompt
        assert "[TODO]" not in user_prompt

    def test_minimum_techniques(self):
        """Verifica se pelo menos 2 técnicas foram listadas."""
        file_load = load_prompts('prompts/bug_to_user_story_v2.yml')
        file_load = file_load.get('bug_to_user_story_v2', {})
        techniques = ['Few-shot', 'Chain-of-Thought', 'Tree of Thought', 'Skeleton of Thought', 'ReAct', 'Role Prompting']
        techniques_applied = file_load.get('techniques_applied', [])
        matched_techniques = [tech for tech in techniques if any(tech.lower() in ta.lower() for ta in techniques_applied)]
        assert len(matched_techniques) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
