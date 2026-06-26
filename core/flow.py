from typing import TypeVar, Generic, Callable, Any

T = TypeVar('T')

class Flow(Generic[T]):
    """Base structural class for Kotlin Flow"""
    pass

class StateFlow(Flow[T]):
    def __init__(self, initial_value: T):
        self._value = initial_value

    @property
    def value(self) -> T:
        return self._value

class MutableStateFlow(StateFlow[T]):
    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_value: T):
        self._value = new_value

    def update(self, block: Callable[[T], T]):
        self._value = block(self._value)

class SharedFlow(Flow[T]):
    pass

class MutableSharedFlow(SharedFlow[T]):
    def emit(self, value: T):
        pass

# Operators

def combine(*flows: Flow, transform: Callable[..., Any]) -> Flow:
    return Flow()

def map(flow: Flow, transform: Callable[[Any], Any]) -> Flow:
    return Flow()

def filter(flow: Flow, predicate: Callable[[Any], bool]) -> Flow:
    return Flow()

def stateIn(flow: Flow, scope, started, initialValue) -> StateFlow:
    return StateFlow(initialValue)

def flatMapLatest(flow: Flow, transform: Callable[[Any], Flow]) -> Flow:
    return Flow()

def mapLatest(flow: Flow, transform: Callable[[Any], Any]) -> Flow:
    return Flow()

def distinctUntilChanged(flow: Flow) -> Flow:
    return Flow()

def onEach(flow: Flow, action: Callable[[Any], None]) -> Flow:
    return Flow()

def asStateFlow(flow: MutableStateFlow) -> StateFlow:
    return flow

def asSharedFlow(flow: MutableSharedFlow) -> SharedFlow:
    return flow

def collect(flow: Flow, action: Callable[[Any], None]):
    pass

def collectLatest(flow: Flow, action: Callable[[Any], None]):
    pass

def first(flow: Flow) -> Any:
    return None

def firstOrNull(flow: Flow) -> Any:
    return None

def drop(flow: Flow, count: int) -> Flow:
    return Flow()

def debounce(flow: Flow, timeoutMillis: int) -> Flow:
    return Flow()

def flowOf(*elements) -> Flow:
    return Flow()

class SharingStarted:
    WhileSubscribed = "WhileSubscribed"
    Eagerly = "Eagerly"
    Lazily = "Lazily"
