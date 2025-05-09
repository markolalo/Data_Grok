import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
import pandas as pd
from etl import SynchroteamETL

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

# Initialize the ETL class
etl = SynchroteamETL(api_key, api_url, domain)

# Date range for the report
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = '2025-01-01 00:00:00'

# Fetch and process jobs and activities
jobs_data = etl.fetch_jobs(start_date, end_date)
activities_data = etl.fetch_activities(start_date, end_date)

# Process jobs data
if not jobs_data.empty:
    is_valid, issues = etl.validate_data(jobs_data)
    if not is_valid:
        logging.error('Jobs data validation failed with issues:')
        for issue in issues:
            logging.error(issue)
    else:
        logging.info('Jobs data validation passed')
        transformed_jobs = etl.transform_data(jobs_data)
        transformed_jobs.to_csv('jobs.csv', index=False, mode='w')
        logging.info('Jobs data saved to jobs.csv with {} rows'.format(len(transformed_jobs)))
else:
    logging.warning('No job data fetched for the given date range')

# Process activities data
if not activities_data.empty:
    #is_valid, issues = etl.validate_data(activities_data)
    # if not is_valid:
    #     logging.error('Activities data validation failed with issues:')
    #     for issue in issues:
    #         logging.error(issue)
    # else:
    #     logging.info('Activities data validation passed')
        #transformed_activities = etl.transform_data(activities_data)
    activities_data.to_csv('activities.csv', index=False, mode='w')
    logging.info('Activities data saved to activities.csv with {} rows'.format(len(activities_data)))
else:
    logging.warning('No activity data fetched for the given date range')