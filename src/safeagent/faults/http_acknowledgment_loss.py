import httpx
import asyncio


class HTTPAcknowledgmentLossTransport(httpx.AsyncBaseTransport):
    """
    Injects one simulated acknowledgment loss after
    the wrapped transport completes a POST request.
    """

    def __init__(self, wrapped_transport: httpx.AsyncBaseTransport):
        self.wrapped_transport = wrapped_transport
        self.injected = False

    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:

        response = await self.wrapped_transport.handle_async_request(
            request
        )

        if request.method == "POST" and not self.injected:
            self.injected = True

            await response.aclose()

            raise httpx.ReadTimeout(
                "Simulated acknowledgment loss after server processing",
                request=request,
            )

        return response

    async def aclose(self):
        await self.wrapped_transport.aclose()



class HTTPVerificationFailureTransport(httpx.AsyncBaseTransport):
    """
    Injects a simulated timeout when the client attempts
    to verify an operation.

    Other requests are forwarded to the wrapped transport.
    """

    def __init__(self, wrapped_transport: httpx.AsyncBaseTransport):
        self.wrapped_transport = wrapped_transport

    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:

        if (
            request.method == "GET"
            and request.url.path.startswith("/operations/")
        ):
            raise httpx.ReadTimeout(
                "Simulated verification endpoint timeout",
                request=request,
            )

        return await self.wrapped_transport.handle_async_request(
            request
        )

    async def aclose(self):
        await self.wrapped_transport.aclose()




class DelayedVerificationFailureTransport(httpx.AsyncBaseTransport):

    def __init__(
        self,
        wrapped_transport: httpx.AsyncBaseTransport,
        delay_seconds: float = 0.05,
    ):
        if delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")

        self.wrapped_transport = wrapped_transport
        self.delay_seconds = delay_seconds

    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:

        # Inject a timeout only for operation verification.
        if (
            request.method == "GET"
            and request.url.path.startswith("/operations/")
        ):
            await asyncio.sleep(self.delay_seconds)

            raise httpx.ReadTimeout(
                "Simulated delayed verification timeout",
                request=request,
            )

        # IMPORTANT: Forward other requests and return the response.
        return await self.wrapped_transport.handle_async_request(
            request
        )

    async def aclose(self):
        await self.wrapped_transport.aclose()