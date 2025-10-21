"""
CSV Data Connector
Fetches data from CSV files.
"""

import csv
from pathlib import Path
from typing import Dict, List

from .base_connector import BaseConnector, logger


class CSVConnector(BaseConnector):
    """
    Connector for CSV data sources.
    """

    def __init__(self, config: Dict):
        """
        config = {
            'source_path': '/path/to/file.csv',
            'delimiter': ',' (optional),
            'encoding': 'utf-8' (optional)
        }
        """
        super().__init__(config)
        self.source_path = config.get("source_path")
        self.delimiter = config.get("delimiter", ",")
        self.encoding = config.get("encoding", "utf-8")

    def connect(self) -> bool:
        """Validate CSV file exists"""
        try:
            return Path(self.source_path).exists()
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def fetch(self) -> List[Dict]:
        """Fetch CSV data as list of dictionaries"""
        try:
            with open(self.source_path, "r", encoding=self.encoding) as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                self.data = list(reader)

            logger.info(f"Fetched {len(self.data)} records from {self.source_path}")
            return self.data

        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return []

    def disconnect(self) -> bool:
        """No persistent connection to close"""
        return True
