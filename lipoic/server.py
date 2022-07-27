from asyncio import AbstractEventLoop, Protocol
import logging

log = logging.getLogger("lipoic")


class Service(Protocol):
    def connection_made(self, tr):
        self.tr = tr
        self.total = 0

    def data_received(self, data):
        if data:
            log.info(data.decode("utf-8").split("\n")[0])
            self.tr.write(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html\r\n"
                b"\r\n"
                b"Hello World!"
            )
        self.tr.close()


async def start(loop: AbstractEventLoop):
    server = await loop.create_server(Service, "0.0.0.0", 8080)
    log.info("start server")
    await server.wait_closed()


def create_server(loop: AbstractEventLoop):
    """for keep online repl.it server"""
    loop.create_task(start(loop))
