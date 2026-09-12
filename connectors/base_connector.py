from abc import ABC, abstractmethod

class BaseConnector(ABC):

    @abstractmethod
    def fetch(self):
        """
        Return a list of leads.
        """
        pass