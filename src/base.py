import abc


class Strategy(abc.ABC):
    @abc.abstractmethod
    def apply(self, entity):
        pass
