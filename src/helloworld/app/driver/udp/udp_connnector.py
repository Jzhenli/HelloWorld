import asyncio
from typing import Optional, Tuple
from ..connector import Connector
from ...log import logger

class ConnectionClosedError(Exception):
    pass

class AsyncUDPClient(Connector):
    class _UDPProtocol(asyncio.DatagramProtocol):
        def __init__(self, client):
            self.client:AsyncUDPClient = client
            self.transport: Optional[asyncio.DatagramTransport] = None

        def connection_made(self, transport):
            self.transport = transport
            logger.debug(f"Connection made: {transport}")

        def datagram_received(self, data: bytes, addr: Tuple[str, int]):
            try:
                self.client._receive_queue.put_nowait((data, addr))
            except asyncio.QueueFull:
                logger.warning(f"Receive queue full, dropping datagram from {addr}")

        def error_received(self, exc: Exception):
            logger.error(f"Protocol error: {exc}")
            self.client._receive_queue.put_nowait(exc)
            if self.transport:
                self.transport.close()

        def connection_lost(self, exc: Optional[Exception]):
            logger.info(f"Connection lost: {exc}")
            if exc is None:
                self.client._receive_queue.put_nowait(ConnectionClosedError())
            else:
                self.client._receive_queue.put_nowait(exc)

    def __init__(self, host: str, port: int, queue_size: int = 1024):
        self.host = host
        self.port = port
        self._queue_size = queue_size
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._protocol: Optional[AsyncUDPClient._UDPProtocol] = None
        self._receive_queue = asyncio.Queue(maxsize=self._queue_size)

    async def open(self):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: self._UDPProtocol(self),
            remote_addr=(self.host, self.port)
        )
        self._transport = transport
        self._protocol = protocol
        logger.info(f"Connected to {self.host}:{self.port}")

    async def send(self, data: bytes):
        if not self._transport:
            raise RuntimeError("Connection not established. Call 'open' first.")
        try:
            self._transport.sendto(data)
            logger.debug(f"Sent {len(data)} bytes to {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Send error: {e}")
            raise e

    async def receive(self, timeout: float = 1.0) -> Tuple[bytes, Tuple[str, int]]:
        if not self._protocol:
            logger.error("Receive called before connection established.")
            raise RuntimeError("Connection not established. Call 'open' first.")

        try:
            item = await asyncio.wait_for(self._receive_queue.get(), timeout=timeout)
            if isinstance(item, Exception):
                logger.error(f"Received exception: {item}")
                raise item
            logger.debug(f"Received {len(item[0])} bytes from {item[1][0]}:{item[1][1]}")
            return item
        except asyncio.TimeoutError:
            logger.error(f"Receive timed out after {timeout} seconds")
            raise TimeoutError("Receive operation timed out")

    def close(self):
        if self._transport:
            logger.info(f"Closing connection to {self.host}:{self.port}")
            self._transport.close()
        if self._protocol:
            self._receive_queue.put_nowait(ConnectionClosedError())
        self._transport = None
        self._protocol = None

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except Exception as e:
            logger.error(f"Error during close: {e}")
        if exc_val:
            logger.error(f"Context error: {exc_val}")


async def main():
    commands = {
        "init": "init,10,20,23,25,2,1",  # 最低温度、最高温度、房间面积、人数、喜好
        "start":"start",
        "stop":"stop",
        "get_regular_temp": "get_temp,regular",
        "get_ai_temp": "get_temp,predict",
        "get_regular_energy":"get_energy,regular",
        "get_ai_energy":"get_energy,predict",
    }
    
    
    async with AsyncUDPClient("127.0.0.1", 12345) as client:
        for cmd in [commands["init"], commands["start"]]:
            await client.send(cmd.encode('utf-8'))
            data, addr = await client.receive()
            print(f"send cmd:{cmd}")
            print(f"Received {data.decode('utf-8')} from {addr}")
            await asyncio.sleep(1)

        for _ in range(10):
            for cmd in [commands["get_regular_temp"], commands["get_ai_temp"], \
                commands["get_regular_energy"],commands["get_ai_energy"]]:
                await client.send(cmd.encode('utf-8'))
                data, addr = await client.receive()
                print(f"send cmd:{cmd}")
                print(f"Received {data.decode('utf-8')} from {addr}")
            await asyncio.sleep(2)

        await client.send(commands["stop"].encode('utf-8'))
        data, addr = await client.receive()
        print(f"Received {data.decode('utf-8')} from {addr}")

if __name__ == "__main__":
    asyncio.run(main())