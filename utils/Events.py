import asyncio
from typing import Callable, Coroutine, Any, Dict, List, Optional


__all__ = ('Events')

CoroFunc = Callable[..., Any]


class Events:
    def __init__(self, call_class: bool = True, class_class_start: Optional[str] = None):
        self._call_class = call_class
        self._class_class_start = class_class_start or 'on_'

        self.extra_events: Dict[str, List[CoroFunc]] = {}

    def add_event_listener(self, func: CoroFunc, name: Optional[str] = None, once: bool = False) -> None:
        name = name or func.__name__

        if not callable(func):
            raise TypeError('func must be callable')

        if once:
            self.once(func, name)
            return

        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def on(self, func: CoroFunc, name: Optional[str] = None, once: bool = False) -> None:
        self.add_event_listener(func, name, once)

    def once(self, func: CoroFunc, name: Optional[str] = None) -> None:
        def _remove_event_listener():
            self.remove_event_listener(func, name)
            self.remove_event_listener(_remove_event_listener, name)
        self.add_event_listener(_remove_event_listener, name)
        self.add_event_listener(func, name)

    def event(self, func: CoroFunc) -> CoroFunc:
        self.add_event_listener(self, func.__name__, func)
        return func

    def listen(self, name: Optional[str] = None, once: bool = False) -> Callable[[CoroFunc], CoroFunc]:
        def decorator(func: CoroFunc) -> CoroFunc:
            self.add_event_listener(func, name, once)
            return func

        return decorator

    def remove_event_listener(self, func: CoroFunc, name: Optional[str] = None) -> None:
        name = name or func.__name__

        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                ...

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self.dispatch(event_name, *args, **kwargs)

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self._dispatch_class_event(event, event_name, *args, **kwargs)
        for event in self.extra_events.get(event_name, []):
            self._schedule_event(event, event_name, *args, **kwargs)

    def _dispatch_class_event(self, event_name: str, *args: Any, **kwargs: Any):
        if not self._call_class:
            return

        method_name = self._class_class_start + event_name

        try:
            coro = getattr(self, method_name)
        except AttributeError:
            ...
        else:
            self._schedule_event(coro, method_name, *args, **kwargs)

    def _schedule_event(
        self,
        coro: CoroFunc,
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if asyncio.iscoroutinefunction(coro):
            asyncio.create_task(
                self._run_async_event(coro, event_name, *args, **kwargs),
                name=f'{self.__class__.__name__}: {event_name}'
            )
            return
        self._run_event(coro, event_name, *args, **kwargs)

    async def _run_async_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            ...
        except Exception as er:
            if event_name != 'error':
                self.dispatch('error', *args, **kwargs, error=er)

    def _run_event(
        self,
        coro: CoroFunc,
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            coro(*args, **kwargs)
        except Exception as er:
            if event_name != 'error':
                self.dispatch('error', *args, **kwargs, error=er)

    @property
    def events_names(self) -> List[str]:
        return self.extra_events.keys()

    @property
    def listener_count(self) -> int:
        return len(self.extra_events.keys())

    @property
    def listeners(self, eventName: str) -> List[CoroFunc]:
        return self.extra_events.get(eventName, [])
