from typing import TypeVar, Generic, Callable, Any

T = TypeVar('T')

class Flow(Generic[T]):
    """Base structural class for Kotlin Flow"""
    
    def map(self, transform: Callable[[Any], Any]) -> 'Flow':
        return self
        
    def filter(self, predicate: Callable[[Any], bool]) -> 'Flow':
        return self
        
    def stateIn(self, scope, started, initialValue) -> 'StateFlow':
        return StateFlow(initialValue)
        
    def flatMapLatest(self, transform: Callable[[Any], 'Flow']) -> 'Flow':
        return self
        
    def mapLatest(self, transform: Callable[[Any], Any]) -> 'Flow':
        return self
        
    def distinctUntilChanged(self) -> 'Flow':
        return self
        
    def onEach(self, action: Callable[[Any], None]) -> 'Flow':
        return self
        
    def collect(self, action: Callable[[Any], None]):
        pass
        
    def collectLatest(self, action: Callable[[Any], None]):
        pass
        
    def drop(self, count: int) -> 'Flow':
        return self
        
    def debounce(self, timeoutMillis: int) -> 'Flow':
        return self
        
    def mapNotNull(self, transform: Callable[[Any], Any]) -> 'Flow':
        return self
        
    def first(self) -> Any:
        return None
        
    def firstOrNull(self) -> Any:
        return None

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

# Free operators
def combine(*flows: Flow, transform: Callable[..., Any]) -> Flow:
    return Flow()

def flowOf(*elements) -> Flow:
    return Flow()

def asStateFlow(flow: MutableStateFlow) -> StateFlow:
    return flow

def asSharedFlow(flow: MutableSharedFlow) -> SharedFlow:
    return flow

class SharingStarted:
    WhileSubscribed = "WhileSubscribed"
    Eagerly = "Eagerly"
    Lazily = "Lazily"
