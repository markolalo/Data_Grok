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
#load_dotenv()
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

# Load or set the last run date
LAST_FETCH_FILE = 'last_fetch.txt'
def get_last_fetch():
    try:
        with open(LAST_FETCH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return '2025-01-01 00:00:00'  # Default to a date if no file exists
def save_last_fetch(date):
    with open(LAST_FETCH_FILE, 'w') as f:
        f.write(date)

# Set date range for incremental fetch
last_fetch = get_last_fetch()
end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
params = {
    'dateFrom': last_fetch, # Use the last fetch date
    'dateTo': end_date,
    'pageSize': 100
}

# Fetch new or updated jobs
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
    new_df = pd.DataFrame(all_jobs)
    
    # Flatten the JSON data
    flatener = JsonFlatener(key_to_extract='name')
    columns_to_flatten = ['technician', 'customer', 'site', 'type', 'createdBy']
    for column in columns_to_flatten:
        new_df[column] = new_df[column].apply(flatener.flatten_json)

    # Validate the data
    is_valid, issues = validate_data(new_df)
    if not is_valid:
        logging.error('Data validation failed with issues:')
        for issue in issues:
            logging.error(issue)
    else:
        logging.info('Data validation passed')

    # Save the data to a CSV file
    try:
        existing_df = pd.read_csv('jobs.csv')
        logging.info('Loaded existing jobs.csv')
    except FileNotFoundError:
        existing_df = pd.DataFrame()
        logging.info('No existing jobs.csv found, creating a new one')

    # Append new data to the existing DataFrame
    if not existing_df.empty:
        # Convert 'id' to string to avoid merging issues
        existing_df['id'] = existing_df['id'].astype(str)
        new_df['id'] = new_df['id'].astype(str)

        # Merge the new data with the existing data
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['id'], keep='last')

    else:
        combined_df = new_df

    # Save the combined DataFrame to CSV
    combined_df.to_csv('jobs.csv', index=False, mode='w')
    logging.info('Data saved to jobs.csv with {} rows'.format(len(combined_df)))

    # Update the last fetch date
    latest_timestamp = new_df['dateModified'].max() if 'dateModified' in new_df.columns else end_date
    save_last_fetch(latest_timestamp)
    logging.info(f'Last fetch date updated to {latest_timestamp}')

    # ---- Data Analysis ----
    logging.info('Starting data analysis')

    # convert timestamps to datetime objects
    combined_df['actualStart'] = pd.to_datetime(combined_df['actualStart'], errors='coerce')
    combined_df['actualEnd'] = pd.to_datetime(combined_df['actualEnd'], errors='coerce')
    combined_df['scheduledStart'] = pd.to_datetime(combined_df['scheduledStart'], errors='coerce')
    #Limit time to year 2025
    combined_df = combined_df[combined_df['scheduledStart'] >= '2025-01-01']
    top_techs = combined_df['technician'].value_counts().head(10).index.tolist()
    
    # Jobs Over Time (by Day)
    jobs_by_day = combined_df.groupby(combined_df['scheduledStart'].dt.date).size().reset_index(name='job_count')
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=jobs_by_day, x='scheduledStart', y='job_count', marker='o')
    plt.title('Jobs Scheduled Over Time - Daily', fontsize=9)
    plt.xlabel('Date', fontsize=9)
    plt.ylabel('Jobs', fontsize=9)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('jobs_by_day.png', dpi=300) #comment to not save the plot
    #plt.show()
    logging.info('Saved jobs_by_day.png')

    # Technician workload Trends (Jobs per Technician over Time)
    workload = combined_df.groupby(['technician', combined_df['scheduledStart'].dt.to_period('M').dt.to_timestamp()]).size().reset_index(name='job_count')
    workload = workload[workload['technician'].isin(top_techs)] # Filter for top technicians
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=workload, x='scheduledStart', y='job_count', hue='technician', marker='o')
    plt.title('Technician Workload Trends - Monthly', fontsize=9)
    plt.xlabel('Date', fontsize=9)
    plt.ylabel('Jobs', fontsize=9)
    plt.xticks(rotation=45)
    plt.legend(title='Technician', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('technician_workload.png', dpi=300) #comment to not save the plot
    #plt.show()
    logging.info('Saved technician_workload.png')

    logging.info('Data analysis completed successfully')

else:
    logging.warning(f'Error: {response.status_code} - {response.text}') # Print the error message
    