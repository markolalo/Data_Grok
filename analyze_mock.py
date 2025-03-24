import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the mock data from the CSV file
df = pd.read_csv('mock_data.csv') 

# Convert start_time and end_time to datetime objects
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])

# Calculate the duration of each job in hours
df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600

# Filter the data for completed jobs
completed_jobs = df[df['status'] == 'completed']

# Analysis 1: Average duration of completed jobs by technician
avg_duration = completed_jobs.groupby('technician')['duration'].mean()
print('Average duration of completed jobs by technician:')
print(avg_duration)
avg_duration.plot(kind='bar', title='Avg Job Duration by Technician', color='skyblue')
plt.ylabel('Hours)')
plt.xlabel('Technician')
plt.tight_layout()
plt.savefig('avg_duration_advancedn.png')
plt.show()

# Analysis 2: Jobs completed per technician
job_count = completed_jobs['technician'].value_counts()
print('\nNumber of jobs completed by each technician:')
print(job_count)
job_count.plot(kind='pie', title='Jobs Completed by Technician', autopct='%1.1f%%')
plt.ylabel('') # Hide the y-label
plt.savefig('jobs_completed_by_technician.png')
plt.show()

# Analysis 3: Status breakdown
status_breakdown = df.groupby(['technician', 'status']).size().unstack().fillna(0)
print('\nStatus breakdown by technician:')
print(status_breakdown)
status_breakdown.plot(kind='bar', stacked=True, title='Status Breakdown by Technician', colormap='tab20')
plt.ylabel('Number of Jobs')
plt.xlabel('Technician')
plt.tight_layout()
plt.legend(title='Status', bbox_to_anchor=(1.05, 1), loc='upper right')
plt.savefig('status_breakdown.png')
plt.show()