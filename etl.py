# This module will handle ETL (Extract, Transform, Load) operations for Synchroteam data.

import requests
import base64
import logging
import pandas as pd
from datetime import datetime, timedelta
from JsonFlatener import JsonFlatener

class SynchroteamETL:
    def __init__(self, api_key, api_url, domain):
        if not api_key or not api_url:
            raise ValueError('API key or URL not set')

        self.api_url = api_url
        self.auth_encoded = base64.b64encode(f'{domain}:{api_key}'.encode()).decode('utf-8')
        self.logger = logging.getLogger(__name__)

    def fetch_jobs(self, start_date, end_date):
        jobs_url = f'{self.api_url}/job/list'
        params = {
            'dateFrom': start_date,
            'dateTo': end_date,
            'pageSize': 100
        }

        all_jobs = []
        page = 1

        while True:
            params['page'] = page
            try:
                response = requests.get(jobs_url, headers={'Authorization': f'Basic {self.auth_encoded}'}, params=params)
                response.raise_for_status()
                data = response.json()
                jobs = data.get('data', [])
                if not jobs:
                    self.logger.info('No more data available')
                    break
                all_jobs.extend(jobs)
                self.logger.info(f'Fetched page {page} with {len(jobs)} jobs')
                page += 1
            except requests.exceptions.HTTPError as err:
                self.logger.error(f'Error on page {page}: {response.status_code} - {response.text}')
                break

        return pd.DataFrame(all_jobs)

    def validate_data(self, df):
        issues = []
        missing_technicians = df['technician'].isnull() | (df['technician'] == 'Unknown')
        if missing_technicians.any():
            issues.append(f'Found {missing_technicians.sum()} rows with missing or unknown technicians')
            self.logger.warning(issues[-1])

        df['scheduledStart'] = pd.to_datetime(df['scheduledStart'], errors='coerce')
        invalid_dates = df['scheduledStart'].isnull()
        if invalid_dates.any():
            issues.append(f'Found {invalid_dates.sum()} rows with invalid scheduleStart dates')
            self.logger.warning(issues[-1])

        return len(issues) == 0, issues

    def transform_data(self, df):
        flatener = JsonFlatener(key_to_extract='name')
        for column in ['technician', 'customer', 'site', 'type', 'createdBy']:
            df[column] = df[column].apply(flatener.flatten_json)
        return df