from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import base64
import logging
from api import SynchroteamAPI
from datetime import datetime

# --- Setup Logging ---
logging.basicConfig(
    filename='synchroteam.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# --- Load Environment Variables ---
load_dotenv()
baseurl = os.getenv('API_URL')
api_key = os.getenv('API_KEY')
domain = os.getenv('DOMAIN')

# --- Validate Environment Variables ---
if not baseurl or not api_key or not domain:
    logging.error("Missing required environment variables: API_KEY, API_URL, or DOMAIN")
    raise ValueError("API_KEY, API_URL, or DOMAIN not set in .env file")

# -------Initialize API Authentication -------
auth_string = f'{domain}:{api_key}'
auth_encoded = base64.b64encode(auth_string.encode()).decode('utf-8')
# -------Initialize SynchroteamAPI -------
api = SynchroteamAPI(auth_encoded, baseurl)

app = Flask(__name__)

@app.route('/')
def home():
    return "<a href='/jobs'>View Jobs</a>"

@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
    Fetch jobs from Synchroteam API and render them in a template.
    Supports optional start_date and end_date query parameters.
    """
    start_date = request.args.get('start_date', '2025-01-01 00:00:00')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    params = {
        'dateFrom': start_date,
        'dateTo': end_date,
        'pageSize': 100
    }
    logging.info(f"Fetching jobs from {start_date} to {end_date}")
    try:
        data = api.call('GET', 'job/list', params=params)
        jobs = data.get('data', [])
        logging.info(f"Fetched {len(jobs)} jobs")
        return render_template('jobs.html', jobs=jobs, start_date=start_date, end_date=end_date)
    except Exception as e:
        logging.error(f"Error fetching jobs: {str(e)}")
        return f"Error fetching jobs: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
        