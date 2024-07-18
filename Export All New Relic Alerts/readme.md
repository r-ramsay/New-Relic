# New Relic Alert Conditions Exporter
This Python script exports the alert conditions for New Relic NRQL Alerts and saves each condition as an individual JSON file.

## Prerequisites

- Python 3.6 or higher
- `requests` library
- `python-dotenv` library

## Setup

1. Clone this repository or download the script files to your local machine.

2. Create a virtual environment (optional but recommended):

   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

### Install the required libraries:

pip install requests python-dotenv


### env
NEW_RELIC_API_KEY=your_new_relic_api_key_here
ACCOUNT_ID=new_relic_account_id_here

Create a .env file in the project directory and add your New Relic API key & Account ID

## Run the script:

python export_alerts.py

The script will fetch all alert conditions from your New Relic account and save each condition as an individual JSON file in the alert_conditions directory.

## How It Works
Fetch Alert Conditions: The script queries New Relic's GraphQL API to fetch all NRQL alert conditions.
Save Conditions: Each alert condition is saved as an individual JSON file with sanitized filenames to avoid issues with special characters.

## This will output something like:


Starting the alert conditions export process...
Fetching all alert conditions...
Found 7 alert conditions.
Saved alert condition to alert_conditions/Condition_1.json
Saved alert condition to alert_conditions/Condition_2.json
...


## Troubleshooting
Ensure your New Relic API key has the necessary permissions to access alert conditions.
Verify your .env file is correctly set up with the NEW_RELIC_API_KEY and ACCOUNT_ID.
Check for any error messages printed by the script to diagnose issues.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for review.
