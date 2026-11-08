from typing import Any, Callable


class AcknowledgmentLossInjector:
    """
    Simulates a successful operation whose response is lost.

    The wrapped operation executes first.
    The injector then raises TimeoutError to the caller.
    """

    def __init__(self) -> None:
        self._inject_next = True

    def execute(
        self,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        result = operation(*args, **kwargs)

        if self._inject_next:
            self._inject_next = False

            raise TimeoutError(
                "Simulated timeout: operation completed, "
                "but acknowledgment was lost."
            )

        return result