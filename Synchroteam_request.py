import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import time
import base64
import json
import pandas as pd
from api import SynchroteamAPI
from JsonFlatener import JsonFlatener

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('API_KEY')
api_url = os.getenv('API_URL')
domain = os.getenv('DOMAIN')

# Check if credentials are set
if not api_key or not api_url:
    raise ValueError('API key or URL not set')

# Combine domain and api_key for basic authentication
auth_string = f'{domain}:{api_key}'
auth_encoded = base64.b64encode(auth_string.encode()).decode('utf-8')

# Initialize the API class
api = SynchroteamAPI(auth_encoded)
# Date range for the report: Last 3 days
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = '2025-01-01 00:00:00'
params = {
    'dateFrom': start_date,
    'dateTo': end_date,
    'pageSize': 100
}

# Make the API call
jobs_url = f'{api_url}/job/list'
#payload = {}
all_jobs = []
page = 1

while True:
    params['page'] = page # Set the page number
    try:
        response = api.call('GET', jobs_url, params=params)
        response.raise_for_status() # Raise an exception for 4xx/5xx status codes
        data = response.json()
        jobs = data.get('data', []) # Extract the 'data' field from the
        if not jobs:
            print('No more data available')
            break
        all_jobs.extend(jobs)
        print(f'Page {page}: {len(jobs)} jobs')
        page += 1
        time.sleep(1) # Sleep for 1 second to avoid rate limiting

    except requests.exceptions.HTTPError as err:
        print(f'Error on page {page}: {response.status_code} - {response.text}')
        break

#Check if the response is valid
if all_jobs:
    df = pd.DataFrame(all_jobs)
    
    # Flatten the JSON data
    flatener = JsonFlatener(key_to_extract='name')
    df['technician'] = df['technician'].apply(flatener.flatten_json)
    df['customer'] = df['customer'].apply(flatener.flatten_json)
    df['site'] = df['site'].apply(flatener.flatten_json)
    df['type'] = df['type'].apply(flatener.flatten_json)
    df['createdBy'] = df['createdBy'].apply(flatener.flatten_json)

    # Save the data to a CSV file
    df.to_csv('jobs.csv', index=False, mode='w')
    print('Data saved to jobs.csv with {} rows'.format(len(df)))

else:
    print(f'Error: {response.status_code} - {response.text}') # Print the error message
    