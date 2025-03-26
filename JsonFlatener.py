import json
import pandas as pd

class JsonFlatener:
    def __init__(self, key_to_extract='name'):
        self.key_to_extract = key_to_extract

    def flatten_json(self, json_data):
        # Handle missing data
        if pd.isna(json_data):
            return 'Unknown'
        
        # Case 1: If json_data is already a dictionary
        if isinstance(json_data, dict):
            return json_data.get(self.key_to_extract, 'Unknown')
        
        # Case 2: If json_data is a string, parse it as JSON
        if isinstance(json_data, str):
            try:
                json_data = json_data.replace("'", '"')
                data = json.loads(json_data)
                return data.get(self.key_to_extract, 'Unknown')
            except json.JSONDecodeError:
                print(f'Error parsing JSON data: {json_data}')
                return 'Unknown'
            
        # Default case: Return 'Unknown' for unsupported data types
        return 'Unknown'