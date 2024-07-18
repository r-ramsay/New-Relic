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
    print("Fetching all synthetic monitors...")
    query = """
    {
      actor {
        entitySearch(query: "domain = 'SYNTH' AND type = 'MONITOR'") {
          results {
            entities {
              ... on SyntheticMonitorEntityOutline {
                guid
                name
                accountId
                monitorType
                tags {
                  key
                  values
                }
              }
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
    if response.status_code != 200:
        print(f"Error fetching synthetic monitors: {response.status_code} - {response.text}")
        return None

    response_data = response.json()
    if 'errors' in response_data:
        print(f"Errors in response: {response_data['errors']}")
        return None

    if 'data' in response_data and 'actor' in response_data['data'] and 'entitySearch' in response_data['data']['actor'] and 'results' in response_data['data']['actor']['entitySearch']:
        monitors = response_data['data']['actor']['entitySearch']['results']['entities']
        print(f"Found {len(monitors)} synthetic monitors.")
        return monitors
    else:
        print("No monitors found or there was an error in the response data structure.")
        print(response_data)
        return None

def get_synthetic_script(monitor_guid, account_id):
    print(f"Fetching script for monitor GUID: {monitor_guid}")
    query = """
    query($accountId: Int!, $monitorGuid: EntityGuid!) {
      actor {
        account(id: $accountId) {
          synthetics {
            script(monitorGuid: $monitorGuid) {
              text
            }
          }
        }
      }
    }
    """
    variables = {
        "accountId": account_id,
        "monitorGuid": monitor_guid
    }
    response = requests.post(
        'https://api.newrelic.com/graphql',
        headers=HEADERS,
        json={'query': query, 'variables': variables}
    )
    if response.status_code != 200:
        print(f"Error fetching synthetic script for GUID {monitor_guid}: {response.status_code} - {response.text}")
        return None

    response_data = response.json()
    if 'errors' in response_data:
        print(f"Errors in response: {response_data['errors']}")
        return None

    if 'data' in response_data and 'actor' in response_data['data'] and 'account' in response_data['data']['actor'] and 'synthetics' in response_data['data']['actor']['account'] and 'script' in response_data['data']['actor']['account']['synthetics']:
        return response_data['data']['actor']['account']['synthetics']['script']
    else:
        print(f"Error fetching synthetic script for GUID {monitor_guid}: {response_data}")
        return None

def save_synthetic_script(script_text, file_name):
    try:
        with open(file_name, 'w') as file:
            file.write(script_text)
        print(f"Saved synthetic script to {file_name}")
    except Exception as e:
        print(f"Error saving synthetic script to {file_name}: {e}")

def main():
    print("Starting the synthetic script export process...")
    monitors = get_all_synthetic_monitors()
    if monitors is None or len(monitors) == 0:
        print("No monitors found or there was an error fetching monitors.")
        return

    for monitor in monitors:
        guid = monitor['guid']
        name = monitor['name']
        account_id = monitor['accountId']
        monitor_type = monitor['monitorType']
        
        if monitor_type in ['SCRIPT_BROWSER', 'SCRIPT_API']:
            print(f"Exporting synthetic script: {name} (GUID: {guid})")
            
            # Fetch and save the script data
            script_data = get_synthetic_script(guid, account_id)
            if script_data and 'text' in script_data:
                script_text = script_data['text']
                # Sanitize the file name to avoid issues with special characters
                sanitized_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                file_name = f"{sanitized_name}.txt"
                save_synthetic_script(script_text, file_name)

if __name__ == "__main__":
    main()
