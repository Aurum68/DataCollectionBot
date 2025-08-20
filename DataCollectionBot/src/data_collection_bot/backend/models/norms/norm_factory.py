from typing import Type

from src.data_collection_bot.backend.utils.register_factory import RegisterFactory
from .norm import Norm


class NormFactory(RegisterFactory[Norm]):
    _register: dict[str, Type[Norm]] = {}