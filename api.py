import requests
from typing import Dict, Any

class SynchroteamAPI:
    """
    A class to interact with the Synchroteam API.
    
    Attributes:
        api_key (str): The API key for authentication.
    """
    
    def __init__(self, api_key: str) -> None:
        """
        Initializes the SynchroteamAPI with the provided API key.
        
        Args:
            api_key (str): The API key for authentication.
        """
        self.api_key = api_key

    def call(self, type: str, url: str, params: Dict[str, Any] = None) -> requests.Response:
        """
        Makes an API call to the specified URL with the given request type.
        
        Args:
            type (str): The HTTP method to use for the request (e.g., 'GET', 'POST').
            url (str): The URL to send the request to.
            params (Dict[str, Any], optional): The parameters to include in the request.
        
        Returns:
            requests.Response: The response object from the API call.
        """
        headers = {
            'content-type': 'application/json',
            'authorization': f'Basic {self.api_key}',
            'accept': 'application/json',
            'cache-control': 'no-cache'
        }
        return requests.request(type, url, headers=headers, params=params)