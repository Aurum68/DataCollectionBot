from typing import TypeVar, Generic, Callable, Type

T = TypeVar('T')

class RegisterFactory(Generic[T]):
   # _register: dict[str, Type[T]] = {}


    @classmethod
    def register(cls, rule: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(clazz: Type[T]) -> Type[T]:
            cls._register[rule] = clazz
            return clazz

        return decorator


    @classmethod
    def get_class(cls, rule: str) -> Type[T]:
        clazz = cls._register[rule]
        if clazz is None: raise ValueError(f'{rule} is not registered')
        return clazz


    @classmethod
    def create(cls, rule: str, text: str) -> T:
        clazz = cls.get_class(rule)
        return clazz(text)