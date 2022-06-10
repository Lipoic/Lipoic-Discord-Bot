import asyncio
from typing import Callable, Coroutine, Any, Dict, List, Optional


__all__ = ('Events')

CoroFunc = Callable[..., Any]


class Events:
    def __init__(self):
        self.extra_events: Dict[str, List[CoroFunc]] = {}

    def add_event_listener(self, func: CoroFunc, name: Optional[str] = None, /, once: bool = False) -> None:
        name = name or func.__name__

        if once:
            self.once(func, name)
            return

        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def remove_event_listener(self, func: CoroFunc, name: Optional[str] = None) -> None:
        name = name or func.__name__

        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                ...

    def once(self, func: CoroFunc, name: Optional[str] = None) -> None:
        self.add_event_listener(
            lambda: self.remove_event_listener(func, name), name
        )
        self.add_event_listener(func, name)

    def on(self, func: CoroFunc, name: Optional[str] = None) -> None:
        self.add_event_listener(func, name)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self.dispatch(event_name, *args, **kwargs)

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        event_name = f'on_{event_name}'
        for event in self.extra_events.get(event_name, []):
            self._schedule_event(event, event_name, *args, **kwargs)

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
