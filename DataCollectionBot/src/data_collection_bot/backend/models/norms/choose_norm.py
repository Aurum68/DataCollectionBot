from src.data_collection_bot.backend.utils.rule_enum import Rules
from .norm import Norm
from .norm_factory import NormFactory


@NormFactory.register(Rules.CHOOSE.name)
class ChooseNorm(Norm):
    def __init__(self, raw: str):
        super().__init__(raw)
        clean: str = raw.strip()
        if not self.can_parse(raw): return

        self.norms: list[str] = clean.split('/')


    @classmethod
    def can_parse(cls, raw: str) -> bool:
        clean: str = (raw or '').strip().lower()

        if not clean:
            return False

        items: list[str] = [x.strip() for x in clean.split(';')]
        return any(items) and all(len(x) > 0 for x in items)


    def is_norm(self, value: str) -> bool:
        return value in self.norms