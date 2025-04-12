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

# --- Setup Logging ---
logging.basicConfig(
    filename='synchroteam.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Load Environment Variables ---
load_dotenv()
api_key = os.getenv('API_KEY')
api_url = os.getenv('API_URL')
domain = os.getenv('DOMAIN')

# Log the loaded API_URL for debugging
logging.info(f"Loaded API_URL from .env: {api_url}")

# --- Validate Environment Variables ---
if not api_key or not api_url or not domain:
    logging.error("Missing required environment variables: API_KEY, API_URL, or DOMAIN")
    raise ValueError("API_KEY, API_URL, or DOMAIN not set in .env file")

# Ensure the API URL is valid
if not api_url or not api_url.startswith('http'):
    raise ValueError("Invalid API_URL in .env file. Ensure it starts with 'http' or 'https'.")

# --- Initialize API Authentication ---
auth_string = f'{domain}:{api_key}'
auth_encoded = base64.b64encode(auth_string.encode()).decode('utf-8')

# --- Initialize SynchroteamAPI ---
api = SynchroteamAPI(auth_encoded, api_url)

# --- Define API Parameters ---
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = '2025-01-01 00:00:00'
params = {
    'dateFrom': start_date,
    'dateTo': end_date,
    'pageSize': 100
}
jobs_url = 'job/list'  # Use relative endpoint
all_jobs = []
page = 1

# --- Fetch Data from API ---
logging.info("Starting API data fetch")
while True:
    params['page'] = page  # Set the page number
    try:
        # Make the API call
        response = api.call('GET', jobs_url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        data = response.json()
        jobs = data.get('data', [])  # Extract the 'data' field
        if not jobs:
            logging.info('No more data available')
            break
        all_jobs.extend(jobs)
        logging.info(f'Fetched page {page} with {len(jobs)} jobs')
        page += 1
        time.sleep(1)  # Sleep for 1 second to avoid rate limiting

    except requests.exceptions.ConnectionError as err:
        logging.error(f"Connection error on page {page}: {err}")
        break
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error on page {page}: {err.response.status_code} - {err.response.text}")
        break
    except Exception as err:
        logging.error(f"Unexpected error: {err}")
        break

# --- Data Validation Function ---
def validate_data(df):
    issues = []
    # Check for missing technicians
    missing_technicians = df['technician'].isnull() | (df['technician'] == 'Unknown')
    if missing_technicians.any():
        issues.append(f"Found {missing_technicians.sum()} rows with missing or unknown technicians")
        logging.warning(issues[-1])

    # Check for invalid dates
    df['scheduledStart'] = pd.to_datetime(df['scheduledStart'], errors='coerce')
    invalid_dates = df['scheduledStart'].isnull()
    if invalid_dates.any():
        issues.append(f"Found {invalid_dates.sum()} rows with invalid scheduledStart dates")
        logging.warning(issues[-1])
    return len(issues) == 0, issues

# --- Process and Analyze Data ---
if all_jobs:
    df = pd.DataFrame(all_jobs)
    
    # Flatten JSON fields
    flattener = JsonFlatener(key_to_extract='name')
    for column in ['technician', 'customer', 'site', 'type', 'createdBy']:
        df[column] = df[column].apply(flattener.flatten_json)

    # Validate data
    is_valid, issues = validate_data(df)
    if not is_valid:
        logging.error("Data validation failed with issues:")
        for issue in issues:
            logging.error(issue)
    else:
        logging.info("Data validation passed")

    # Save to CSV
    df.to_csv('jobs.csv', index=False, mode='w')
    logging.info(f"Data saved to jobs.csv with {len(df)} rows")

    # --- Data Analysis ---
    logging.info("Starting data analysis")

    # Convert timestamps
    df['actualStart'] = pd.to_datetime(df['actualStart'], errors='coerce')
    df['actualEnd'] = pd.to_datetime(df['actualEnd'], errors='coerce')
    df['scheduledStart'] = pd.to_datetime(df['scheduledStart'], errors='coerce')
    df = df[df['scheduledStart'] >= '2025-01-01']
    top_techs = df['technician'].value_counts().head(10).index.tolist()

    # Jobs Over Time (Daily)
    jobs_by_day = df.groupby(df['scheduledStart'].dt.date).size().reset_index(name='job_count')
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=jobs_by_day, x='scheduledStart', y='job_count', marker='o')
    plt.title('Jobs Scheduled Over Time - Daily', fontsize=9)
    plt.xlabel('Date', fontsize=9)
    plt.ylabel('Jobs', fontsize=9)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('jobs_by_day.png', dpi=300)
    logging.info("Saved jobs_by_day.png")

    # Technician Workload Trends (Monthly)
    workload = df.groupby(['technician', df['scheduledStart'].dt.to_period('M').dt.to_timestamp()]).size().reset_index(name='job_count')
    workload = workload[workload['technician'].isin(top_techs)]
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=workload, x='scheduledStart', y='job_count', hue='technician', marker='o')
    plt.title('Technician Workload Trends - Monthly', fontsize=9)
    plt.xlabel('Date', fontsize=9)
    plt.ylabel('Jobs', fontsize=9)
    plt.xticks(rotation=45)
    plt.legend(title='Technician', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('technician_workload.png', dpi=300)
    logging.info("Saved technician_workload.png")

    logging.info("Data analysis completed successfully")
else:
    logging.warning("No jobs fetched. Check API credentials, URL, or parameters.")
    sys.exit(1)