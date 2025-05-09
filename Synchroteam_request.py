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

# Fetch and process data
data = etl.fetch_jobs(start_date, end_date)
if not data.empty:
    is_valid, issues = etl.validate_data(data)
    if not is_valid:
        logging.error('Data validation failed with issues:')
        for issue in issues:
            logging.error(issue)
    else:
        logging.info('Data validation passed')
        data = etl.transform_data(data)
        data.to_csv('jobs.csv', index=False, mode='w')
        logging.info('Data saved to jobs.csv with {} rows'.format(len(data)))
else:
    logging.warning('No data fetched for the given date range')

