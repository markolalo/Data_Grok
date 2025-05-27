# Data Analysis Project

This project contains various scripts and tools for analyzing and processing data.

## Project Structure

```
.env
.gitignore
analyze_mock.py
api.py
avg_duration_advancedn.png
avg_duration_by_technician.png
jobs_completed_by_technician.png
jobs_data.csv
jobs.csv
jobs.ipynb
JsonFlatener.py
mock_data.csv
mock.py
README.md
status_breakdown.png
Synchroteam_request.py
__pycache__/
Grok/
```

## Key Components

### JsonFlatener

The `JsonFlatener` class, located in [JsonFlatener.py](JsonFlatener.py), is designed to extract specific keys from JSON data. It handles various cases, including:

- Missing data
- JSON strings
- Dictionaries

#### Example Usage

```python
from JsonFlatener import JsonFlatener

# Initialize the JsonFlatener with the key to extract
flatener = JsonFlatener(key_to_extract='name')

# Flatten a JSON dictionary
result = flatener.flatten_json({'name': 'John Doe', 'age': 30})
print(result)  # Output: John Doe

# Flatten a JSON string
result = flatener.flatten_json('{"name": "Jane Doe", "age": 25}')
print(result)  # Output: Jane Doe

# Handle missing or invalid data
result = flatener.flatten_json(None)
print(result)  # Output: Unknown
```

### Other Scripts

- **analyze_mock.py**: Analyze mock data.
- **api.py**: API-related functionality.
- **mock.py**: Generate mock data for testing.
- **Synchroteam_request.py**: Handle Synchroteam API requests.

## Data Files

- **jobs_data.csv** and **jobs.csv**: Contain job-related data.
- **mock_data.csv**: Mock data for testing.

## Visualizations

The project includes several visualizations:
- `avg_duration_advancedn.png`
- `avg_duration_by_technician.png`
- `jobs_completed_by_technician.png`
- `status_breakdown.png`

## Setup

1. Create a virtual environment:
   ```sh
   python -m venv Grok
   ```

2. Activate the virtual environment:
   - On Windows:
     ```sh
     Grok\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source Grok/bin/activate
     ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
