import re
from typing import Protocol, Type

from src.data_collection_bot.backend.utils.rule_enum import Rules
from src.data_collection_bot.backend.utils.register_factory import RegisterFactory


class Validator(Protocol):
    @classmethod
    def validate(cls, text: str) -> bool:
        ...


class ValidatorFactory(RegisterFactory[Validator]):
    _register: dict[str, Type[Validator]] = {}


@ValidatorFactory.register(Rules.NUMBER.name)
class NumberValidator(Validator):
    @classmethod
    def validate(cls, text: str) -> bool:
        try:
            float(text)
            return True
        except ValueError:
            return False


@ValidatorFactory.register(Rules.BLOOD_PRESSURE.name)
class BloodPressureValidator(Validator):
    BLOOD_PRESSURE_REGEX = re.compile(r'^\d{2,3}(\.\d+)?/\d{2,3}(\.\d+)?$')

    @classmethod
    def validate(cls, text: str) -> bool:
        return bool(re.match(cls.BLOOD_PRESSURE_REGEX, text))


@ValidatorFactory.register(Rules.CHOOSE.name)
class EmptyValidator(Validator):
    @classmethod
    def validate(cls, text: str) -> bool:
        return True


