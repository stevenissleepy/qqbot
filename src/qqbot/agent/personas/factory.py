from pathlib import Path

from qqbot.agent.personas.base import Persona


def build_personas() -> dict[str, Persona]:
    return {
        path.stem: Persona(path.read_text(encoding="utf-8").strip())
        for path in Path(__file__).parent.glob("*.txt")
    }
