from abc import ABC, abstractmethod


class BaseDevice(ABC):

    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def handle_cmd(self, *args):
        pass

    @abstractmethod
    async def sample(self):
        pass


