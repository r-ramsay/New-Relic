import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your New Relic API key
NEW_RELIC_API_KEY = os.getenv('NEW_RELIC_API_KEY')
HEADERS = {
    'API-Key': NEW_RELIC_API_KEY,
    'Content-Type': 'application/json',
}

def get_all_synthetic_monitors():
    query = """
    {
        actor {
            entitySearch(query: "type='SYNTHETIC_MONITOR'") {
                results {
                    entities {
                        guid
                        name
                    }
                }
            }
        }
    }
    """
    response = requests.post(
        'https://api.newrelic.com/graphql',
        headers=HEADERS,
        json={'query': query}
    )
    response_data = response.json()
    monitors = response_data['data']['actor']['entitySearch']['results']['entities']
    return monitors

def get_synthetic_script(monitor_guid):
    query = """
    query($guid: EntityGuid!) {
        actor {
            account(id: YOUR_ACCOUNT_ID) {
                syntheticMonitor(guid: $guid) {
                    guid
                    name
                    script {
                        text
                    }
                }
            }
        }
    }
    """
    variables = {
        "guid": monitor_guid
    }
    response = requests.post(
        'https://api.newrelic.com/graphql',
        headers=HEADERS,
        json={'query': query, 'variables': variables}
    )
    response_data = response.json()
    
    if 'data' in response_data and 'actor' in response_data['data'] and 'account' in response_data['data']['actor'] and 'syntheticMonitor' in response_data['data']['actor']['account']:
        return response_data['data']['actor']['account']['syntheticMonitor']
    else:
        print(f"Error fetching synthetic script for GUID {monitor_guid}: {response_data}")
        return None

def save_synthetic_script(script_data, file_name):
    try:
        with open(file_name, 'w') as file:
            json.dump(script_data, file, indent=4)
        print(f"Saved synthetic script to {file_name}")
    except Exception as e:
        print(f"Error saving synthetic script to {file_name}: {e}")

def main():
    monitors = get_all_synthetic_monitors()
    for monitor in monitors:
        guid = monitor['guid']
        name = monitor['name']
        print(f"Exporting synthetic script: {name} (GUID: {guid})")
        
        # Fetch and save the script data
        script_data = get_synthetic_script(guid)
        if script_data:
            # Sanitize the file name to avoid issues with special characters
            sanitized_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            json_file_name = f"{sanitized_name}.json"
            save_synthetic_script(script_data, json_file_name)

if __name__ == "__main__":
    main()
