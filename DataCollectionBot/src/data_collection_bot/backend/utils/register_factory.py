from typing import TypeVar, Generic, Callable, Type

T = TypeVar('T')

class RegisterFactory(Generic[T]):
    _register: dict[str, Type[T]] = {}


    @classmethod
    def register(cls, rule: str) -> Callable:
        def decorator(clazz: Type[T]) -> Type[T]:
            cls._register[rule] = clazz
            return clazz

        return decorator


    @classmethod
    def create(cls, text: str) -> T:
        clazz = cls._register[text]
        if clazz is None: raise ValueError(f'{text} is not registered')
        return clazz(text)