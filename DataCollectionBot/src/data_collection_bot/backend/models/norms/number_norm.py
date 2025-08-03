from src.data_collection_bot.backend.utils.rule_enum import Rules
from .norm import Norm
from .norm_factory import NormFactory


@NormFactory.register(Rules.NUMBER.name)
class NumberNorm(Norm):
    def __init__(self, raw: str):
        super().__init__(raw)
        self.clean: str = raw.replace('—', '-').replace('–', '-')
        if not self.can_parse(raw): return

        buf: list[float] = [float(x.strip()) for x in self.clean.split('-')]
        if len(buf) != 2: raise ValueError('Range normalization requires two values')
        self.low, self.high = buf


    @classmethod
    def can_parse(cls, raw: str) -> bool:
        clean = raw.replace('—', '-').replace('–', '-')
        return "-" in clean and '/' not in clean


    def is_norm(self, value: str) -> bool:
        try:
            value = float(value)
            return self.low <= value <= self.high
        except ValueError:
            return False