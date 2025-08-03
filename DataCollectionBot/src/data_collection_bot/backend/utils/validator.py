import re
from typing import Protocol

from src.data_collection_bot.backend.utils.register_factory import RegisterFactory


class Validator(Protocol):
    @classmethod
    def validate(cls, text: str) -> bool:
        ...


class ValidatorFactory(RegisterFactory[Validator]):
    pass


@ValidatorFactory.register('Число')
class NumberValidator(Validator):
    @classmethod
    def validate(cls, text: str) -> bool:
        try:
            float(text)
            return True
        except ValueError:
            return False


@ValidatorFactory.register("Артериальное давление")
class BloodPressureValidator(Validator):
    BLOOD_PRESSURE_REGEX = re.compile(r'^\d{2,3}(\.\d+)?/\d{2,3}(\.\d+)?$')

    @classmethod
    def validate(cls, text: str) -> bool:
        return bool(re.match(cls.BLOOD_PRESSURE_REGEX, text))


@ValidatorFactory.register("Empty")
class EmptyValidator(Validator):
    @classmethod
    def validate(cls, text: str) -> bool:
        return True


