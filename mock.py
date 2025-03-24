import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate mock data
np.random.seed(42)  # Consistent random data
technicians = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
dates = [datetime.now() - timedelta(days=i) for i in range(30)]
data = {
    'job_id': range(1, 101),
    'technician': np.random.choice(technicians, 100),
    'start_time': [d - timedelta(hours=np.random.randint(1, 5)) for d in np.random.choice(dates, 100)],
    'status': np.random.choice(['completed', 'started', 'paused', 'synchronized', 'scheduled', 'created', 'validated', 'cancelled'], 100)
}

# Ensure end_time is always greater than start_time
data['end_time'] = [start + timedelta(hours=np.random.randint(1, 5)) for start in data['start_time']]

# Create a DataFrame from the mock data
df = pd.DataFrame(data)
df.to_csv('mock_data.csv', index=False) # Save the data to a CSV file
print('Mock data generated and saved to mock_data.csv') # Print a message to indicate successful generation