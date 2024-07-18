import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your New Relic API key and account ID
NEW_RELIC_API_KEY = os.getenv('NEW_RELIC_API_KEY')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')

HEADERS = {
    'API-Key': NEW_RELIC_API_KEY,
    'Content-Type': 'application/json',
}

def get_all_alert_conditions(account_id):
    print("Fetching all alert conditions...")
    query = """
    {
      actor {
        account(id: %d) {
          alerts {
            nrqlConditionsSearch {
              nrqlConditions {
                id
                name
                type
                enabled
                description
                nrql {
                  query
                  evaluationOffset
                }
                signal {
                  aggregationWindow
                  aggregationMethod
                  aggregationDelay
                }
                terms {
                  threshold
                  thresholdDuration
                  thresholdOccurrences
                  operator
                  priority
                }
                ... on AlertsNrqlStaticCondition {
                  valueFunction
                }
                ... on AlertsNrqlBaselineCondition {
                  baselineDirection
                }
                violationTimeLimitSeconds
              }
            }
          }
        }
      }
    }
    """ % int(account_id)

    response = requests.post(
        'https://api.newrelic.com/graphql',
        headers=HEADERS,
        json={'query': query}
    )
    if response.status_code != 200:
        print(f"Error fetching alert conditions: {response.status_code} - {response.text}")
        return None

    response_data = response.json()
    if 'errors' in response_data:
        print(f"Errors in response: {response_data['errors']}")
        return None

    if 'data' in response_data and 'actor' in response_data['data'] and 'account' in response_data['data']['actor'] and 'alerts' in response_data['data']['actor']['account'] and 'nrqlConditionsSearch' in response_data['data']['actor']['account']['alerts']:
        conditions = response_data['data']['actor']['account']['alerts']['nrqlConditionsSearch']['nrqlConditions']
        print(f"Found {len(conditions)} alert conditions.")
        return conditions
    else:
        print("No alert conditions found or there was an error in the response data structure.")
        print(response_data)
        return None

def save_alert_condition_to_file(alert_condition, directory='alert_conditions'):
    try:
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Create a valid filename by replacing spaces and other unsafe characters
        file_name = f"{alert_condition['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')}.json"
        file_path = os.path.join(directory, file_name)
        
        with open(file_path, 'w') as file:
            json.dump(alert_condition, file, indent=4)
        print(f"Saved alert condition to {file_path}")
    except Exception as e:
        print(f"Error saving alert condition to {file_name}: {e}")

def main():
    print("Starting the alert conditions export process...")
    if not ACCOUNT_ID:
        print("Account ID is not set. Please check your .env file.")
        return

    alert_conditions = get_all_alert_conditions(ACCOUNT_ID)
    if alert_conditions is None or len(alert_conditions) == 0:
        print("No alert conditions found or there was an error fetching alert conditions.")
        return

    for alert_condition in alert_conditions:
        save_alert_condition_to_file(alert_condition)

if __name__ == "__main__":
    main()
