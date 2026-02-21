from abc import ABC, abstractmethod
from typing import List, Dict


class StoreConnector(ABC):
    """Base abstract class for store connectors.

    Subclasses should implement `search(query)` returning list of dicts.
    """

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        raise NotImplementedError
