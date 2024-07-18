# New Relic Synthetic Script Exporter

This Python script exports the scripts for New Relic Synthetic Monitors (Scripted Browser and Scripted API) and saves them as text files.

## Prerequisites

- Python 3.6 or higher
- `requests` library
- `python-dotenv` library

## Setup

1. Clone this repository or download the script files to your local machine.

2. Create a virtual environment (optional but recommended):

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

###Install the required libraries:

pip install requests python-dotenv
Create a .env file in the project directory and add your New Relic API key:

### env
NEW_RELIC_API_KEY=your_new_relic_api_key_here
Usage
Ensure your .env file is set up with your New Relic API key.

## Run the script:

python export_synthetic_scripts.py

The script will fetch all synthetic monitors from your New Relic account, filter for Scripted Browser and Scripted API monitors, and save each script as a text file in the current directory.

## How It Works
Fetch Synthetic Monitors: The script queries New Relic's GraphQL API to fetch all synthetic monitors.
Filter Monitors: It filters the monitors to only include Scripted Browser and Scripted API types.
Fetch Scripts: For each filtered monitor, the script fetches the script content.
Save Scripts: The scripts are saved as text files with sanitized filenames to avoid issues with special characters.

## This will output something like:


Starting the synthetic script export process...
Fetching all synthetic monitors...
Found 7 synthetic monitors.
Exporting synthetic script: Monitor 1 - Script (GUID: Mzk5Mjg1MXxTWU5USHxNT05JVE9SfDc5ZmUzOGI4LTJiYzItNDE1Mi04OTE1LWQ5YjE5MmQ2YjczMg)
Saved synthetic script to Monitor_1_-_Script.txt


## Troubleshooting
Ensure your New Relic API key has the necessary permissions to access synthetic monitors.
Verify your .env file is correctly set up with the NEW_RELIC_API_KEY.
Check for any error messages printed by the script to diagnose issues.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for review.
