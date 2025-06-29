from abc import ABC, abstractmethod

class Connector(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass



    # @abstractmethod
    # def get_id(self):
    #     pass

    # @abstractmethod
    # def get_name(self):
    #     pass

    # @abstractmethod
    # def get_type(self):
    #     pass

    # @abstractmethod
    # def get_config(self):
    #     pass
