"""
JSON Data Connector
Fetches data from JSON files or JSON APIs.
"""
import json
import requests
from pathlib import Path
from typing import Dict, List
from .base_connector import BaseConnector, logger


class JSONConnector(BaseConnector):
    """
    Connector for JSON data sources (files or HTTP endpoints).
    """

    def __init__(self, config: Dict):
        """
        config = {
            'source_type': 'file' | 'api',
            'source_path': '/path/to/file.json' | 'https://api.example.com/data',
            'headers': {} (optional, for API calls)
        }
        """
        super().__init__(config)
        self.source_type = config.get('source_type', 'file')
        self.source_path = config.get('source_path')
        self.headers = config.get('headers', {})

    def connect(self) -> bool:
        """Validate source availability"""
        try:
            if self.source_type == 'file':
                return Path(self.source_path).exists()
            elif self.source_type == 'api':
                response = requests.head(self.source_path, headers=self.headers, timeout=5)
                return response.status_code < 400
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def fetch(self) -> List[Dict]:
        """Fetch JSON data"""
        try:
            if self.source_type == 'file':
                with open(self.source_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif self.source_type == 'api':
                response = requests.get(self.source_path, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()

            # Normalize to list of dictionaries
            if isinstance(data, dict):
                self.data = [data]
            elif isinstance(data, list):
                self.data = data
            else:
                raise ValueError(f"Unexpected JSON structure: {type(data)}")

            logger.info(f"Fetched {len(self.data)} records from {self.source_path}")
            return self.data

        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return []

    def disconnect(self) -> bool:
        """No persistent connection to close"""
        return True
