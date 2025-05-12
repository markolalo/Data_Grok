# Data_Grok: Synchroteam Analytics Platform

## Overview

A robust data analytics platform designed to process and visualize data from Synchroteam's API. This project provides comprehensive ETL (Extract, Transform, Load) capabilities and generates insightful visualizations for workforce management analytics.

## Features

- **Automated Data Collection**: ETL pipeline for Synchroteam data
- **Advanced Data Processing**: Custom JSON flattening and data transformation
- **Visualization Suite**: Multiple visualization types including:
  - Average Duration Analysis
  - Jobs by Day Distribution
  - Technician Workload Analysis
  - Status Breakdown
  - Completion Rate by Technician

## Project Structure

```
├── etl.py                     # Core ETL implementation
├── Synchroteam_request.py     # API request handler
├── JsonFlatener.py           # JSON data processing utility
├── jobs.ipynb                # Jupyter notebook for job analysis
├── requirements.txt          # Project dependencies
├── *.csv                    # Processed data files
└── *.png                    # Generated visualizations
```

## Getting Started

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/[username]/Data_Grok.git
   cd Data_Grok
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with:
   ```
   API_KEY=your_synchroteam_api_key
   API_URL=your_synchroteam_api_url
   DOMAIN=your_domain
   ```

## Usage

1. **Data Collection**:
   ```bash
   python Synchroteam_request.py
   ```

2. **Data Analysis**:
   - Open `jobs.ipynb` in Jupyter Notebook
   - Execute cells to generate visualizations and insights

## Visualizations

The project generates several visualizations:
- `avg_duration_advanced.png`: Advanced duration analysis
- `jobs_by_day.png`: Daily job distribution
- `technician_workload.png`: Workload analysis by technician
- `status_breakdown.png`: Job status distribution
- `jobs_completed_by_technician.png`: Completion rates

## Dependencies

Key dependencies include:
- pandas: Data manipulation and analysis
- matplotlib/seaborn: Data visualization
- requests: API communication
- python-dotenv: Environment configuration
- Jupyter: Interactive analysis

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
