"""
Connector package initialization
"""
from .base_connector import BaseConnector
from .json_connector import JSONConnector
from .csv_connector import CSVConnector
from .web_scraper import WebScraperConnector

__all__ = [
    'BaseConnector',
    'JSONConnector',
    'CSVConnector',
    'WebScraperConnector'
]
