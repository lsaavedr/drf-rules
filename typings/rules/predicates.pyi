from typing import Any, Callable

class Context(dict):
    args: tuple[Any, ...]
    def __init__(self, args: tuple[Any, ...]) -> None: ...

class Predicate:
    fn: Callable[..., Any]
    num_args: int
    var_args: bool
    name: str
    bind: bool
    def __init__(
        self,
        fn: Predicate | Callable[..., Any],
        name: str | None = None,
        bind: bool = False,
    ) -> None: ...
    def __call__(self, *args, **kwargs) -> Any: ...
    @property
    def context(self) -> Context | None: ...
    def test(self, obj: Any = ..., target: Any = ...) -> bool: ...
    def __and__(self, other) -> Predicate: ...
    def __or__(self, other) -> Predicate: ...
    def __xor__(self, other) -> Predicate: ...
    def __invert__(self) -> Predicate: ...

def predicate(
    fn: Callable[..., Any] | None = None, name: str | None = None, **options
) -> Predicate: ...

always_true: Predicate
always_false: Predicate
always_allow: Predicate
always_deny: Predicate

is_bool_like: Predicate
is_authenticated: Predicate
is_superuser: Predicate
is_staff: Predicate
is_active: Predicate
is_group_member: Predicate
