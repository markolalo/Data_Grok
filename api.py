import requests
from typing import Dict, Any
import logging

class SynchroteamAPI:
    """
    A class to interact with the Synchroteam API.
    """
    
    def __init__(self, api_key: str, base_url: str) -> None:
        """
        Initializes the SynchroteamAPI with the provided API key and base URL.
        """
        if not base_url.startswith('http'):
            raise ValueError("Invalid base_url. Ensure it starts with 'http' or 'https'.")
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        logging.info(f"Initialized SynchroteamAPI with base_url: {self.base_url}")

    def call(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> requests.Response:
        """
        Makes an API call to the specified endpoint with the given request type.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"  # Ensure proper URL construction
        headers = {
            'content-type': 'application/json',
            'authorization': f'Basic {self.api_key}',
            'accept': 'application/json',
            'cache-control': 'no-cache'
        }
        logging.info(f"Making {method} request to {url} with params {params}")
        return requests.request(method, url, headers=headers, params=params)