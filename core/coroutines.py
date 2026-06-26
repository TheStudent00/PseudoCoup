import asyncio
from typing import Callable, Any, Coroutine

class Job:
    def __init__(self, task: asyncio.Task = None):
        self.task = task
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True
        if self.task:
            self.task.cancel()

class Dispatchers:
    IO = "IO"
    Main = "Main"
    Default = "Default"

class CoroutineScope:
    def __init__(self, context=None):
        self.context = context

    def launch(self, block: Callable[[], Any]) -> Job:
        """
        Shim for Kotlin's launch.
        In Python, we expect the transpiler to pass the block as a function.
        """
        # If we are in an event loop, create a task
        try:
            loop = asyncio.get_running_loop()
            if asyncio.iscoroutinefunction(block):
                task = loop.create_task(block())
            else:
                # Run sync functions in thread pool for structural parity, 
                # or just run them directly for the 1:1 audit.
                # For structural 1:1, we just run it directly for now.
                block()
                task = None
            return Job(task)
        except RuntimeError:
            # No loop running, just execute it directly for the shim
            block()
            return Job()

viewModelScope = CoroutineScope(Dispatchers.Main)

def runBlocking(block: Callable[[], Any]):
    if asyncio.iscoroutinefunction(block):
        return asyncio.run(block())
    return block()

def delay(timeMillis: int):
    # In a real async Python execution this would be await asyncio.sleep(timeMillis / 1000.0)
    # But for a synchronous shim or a structural audit, we might just sleep or ignore.
    import time
    time.sleep(timeMillis / 1000.0)

def async_task(block: Callable[[], Any]):
    # Shim for async { }
    pass
