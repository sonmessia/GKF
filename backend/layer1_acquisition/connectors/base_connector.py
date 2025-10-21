"""
Base Data Connector Interface
All data connectors must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    Abstract base class for all data connectors.
    Connectors fetch raw data from various sources.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = []

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to data source"""
        pass

    @abstractmethod
    def fetch(self) -> List[Dict]:
        """Fetch data from source"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to data source"""
        pass

    def validate(self, data: Dict) -> bool:
        """Validate fetched data structure"""
        return bool(data)

    def get_data(self) -> List[Dict]:
        """Return fetched data"""
        return self.data
