import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import time
import logging
import sys
import base64
import json
import pandas as pd
from api import SynchroteamAPI
from JsonFlatener import JsonFlatener
import matplotlib.pyplot as plt
import seaborn as sns

# Set up logging
logging.basicConfig(
    filename='synchroteam.log',
    filemode='a',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

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
            logging.info('No more data available')
            break
        all_jobs.extend(jobs)
        logging.info(f'Fetched page {page} with {len(jobs)} jobs')
        page += 1
        time.sleep(1) # Sleep for 1 second to avoid rate limiting

    except requests.exceptions.HTTPError as err:
        logging.error(f'Error on page {page}: {response.status_code} - {response.text}')
        break

# Data Validation
def validate_data(df):
    issues = []
    # Check for missing technicians
    missing_technicians = df['technician'].isnull() | (df['technician'] == 'Unknown')
    if missing_technicians.any():
        issues.append(f'Found {missing_technicians.sum()} rows with missing or unknown technicians')
        logging.warning(issues[-1])

    # Check for invalid dates
    df['scheduledStart'] = pd.to_datetime(df['scheduledStart'], errors='coerce')
    invalid_dates = df['scheduledStart'].isnull()
    if invalid_dates.any():
        issues.append(f'Found {invalid_dates.sum()} rows with invalid scheduleStart dates')
        logging.warning(issues[-1])
    return len(issues) == 0, issues

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

    # Validate the data
    is_valid, issues = validate_data(df)
    if not is_valid:
        logging.error('Data validation failed with issues:')
        for issue in issues:
            logging.error(issue)
    else:
        logging.info('Data validation passed')

    # Save the data to a CSV file
    df.to_csv('jobs.csv', index=False, mode='w')
    logging.info('Data saved to jobs.csv with {} rows'.format(len(df)))

    # ---- Data Analysis ----
    logging.info('Starting data analysis')

    # convert timestamps to datetime objects
    df['actualStart'] = pd.to_datetime(df['actualStart'], errors='coerce')
    df['actualEnd'] = pd.to_datetime(df['actualEnd'], errors='coerce')
    df['scheduledStart'] = pd.to_datetime(df['scheduledStart'], errors='coerce')
    #Limit time to year 2025
    df = df[df['scheduledStart'] >= '2025-01-01']
    top_techs = df['technician'].value_counts().head(10).index.tolist()
    
    # Jobs Over Time (by Day)
    jobs_by_day = df.groupby(df['scheduledStart'].dt.date).size().reset_index(name='job_count')
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=jobs_by_day, x='scheduledStart', y='job_count', marker='o')
    plt.title('Jobs Scheduled Over Time - Daily', fontsize=9)
    plt.xlabel('Date', fontsize=9)
    plt.ylabel('Jobs', fontsize=9)
    plt.xticks(rotation=0)
    plt.tight_layout()
    #plt.savefig('jobs_by_day.png', dpi=300) #Uncomment to save the plot
    plt.show()
    logging.info('Saved jobs_by_day.png')

    # Technician workload Trends (Jobs per Technician over Time)
    workload = df.groupby(['technician', df['scheduledStart'].dt.to_period('M').dt.to_timestamp()]).size().reset_index(name='job_count')
    workload = workload[workload['technician'].isin(top_techs)] # Filter for top technicians
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=workload, x='scheduledStart', y='job_count', hue='technician', marker='o')
    plt.title('Technician Workload Trends - Monthly', fontsize=9)
    plt.xlabel('Date', fontsize=9)
    plt.ylabel('Jobs', fontsize=9)
    plt.xticks(rotation=45)
    plt.legend(title='Technician', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    #plt.savefig('technician_workload.png', dpi=300) #Uncomment to save the plot
    plt.show()
    logging.info('Saved technician_workload.png')

    logging.info('Data analysis completed successfully')

else:
    logging.warning(f'Error: {response.status_code} - {response.text}') # Print the error message
    