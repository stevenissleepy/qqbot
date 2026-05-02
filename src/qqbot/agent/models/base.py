class ModelClient:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """Return the model reply text."""
        raise NotImplementedError
