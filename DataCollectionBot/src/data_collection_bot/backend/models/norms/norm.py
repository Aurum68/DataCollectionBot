from typing import Protocol


class Norm(Protocol):
    def __init__(self, raw: str):
        ...

    @classmethod
    def can_parse(cls, raw: str) -> bool:
        ...


    def is_norm(self, value: str) -> bool:
        ...