import re

from src.data_collection_bot.backend.utils.rule_enum import Rules
from .norm import Norm
from .norm_factory import NormFactory
from src.data_collection_bot.backend.utils import Validator


@NormFactory.register(Rules.BLOOD_PRESSURE.name)
class BloodPressureNorm(Norm):
    def __init__(self, raw: str):
        super().__init__(raw)
        clean = raw.replace('—', '-').replace('–', '-')
        if not self.can_parse(raw): return

        low_pressure, high_pressure = clean.split('-')

        systolic_low, diastolic_low = low_pressure.split('/')
        systolic_high, diastolic_high = high_pressure.split('/')

        self.systolic_low = float(systolic_low)
        self.diastolic_low = float(diastolic_low)
        self.systolic_high = float(systolic_high)
        self.diastolic_high = float(diastolic_high)


    @classmethod
    def can_parse(cls, raw: str) -> bool:
        clean = raw.replace('—', '-').replace('–', '-')
        regex = re.compile(r'^\d{2,3}(\.\d+)?/\d{2,3}(\.\d+)?-\d{2,3}(\.\d+)?/\d{2,3}(\.\d+)?$')
        return bool(re.match(regex, clean))


    def is_norm(self, value: str) -> bool:
        if not Validator.validate(value): raise ValueError("{value} is not a valid blood pressure".format(value=value))
        systolic, diastolic = value.split('/')
        try:
            systolic = float(systolic)
            diastolic = float(diastolic)
            return (self.systolic_low <= systolic <= self.systolic_high and
                    self.diastolic_low <= diastolic <= self.diastolic_high)
        except ValueError:
            raise ValueError("{value} is not a valid blood pressure".format(value=value))