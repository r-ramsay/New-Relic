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

def get_all_dashboards():
    query = """
    {
        actor {
            entitySearch(query: "type='DASHBOARD'") {
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
    dashboards = response_data['data']['actor']['entitySearch']['results']['entities']
    return dashboards

def get_dashboard_json(dashboard_guid):
    query = """
    query($guid: EntityGuid!) {
        actor {
            entity(guid: $guid) {
                ... on DashboardEntity {
                    guid
                    name
                    pages {
                        name
                        widgets {
                            visualization {
                                id
                                __typename
                            }
                            layout {
                                column
                                row
                                height
                                width
                            }
                            title
                            rawConfiguration
                        }
                    }
                }
            }
        }
    }
    """
    variables = {
        "guid": dashboard_guid
    }
    response = requests.post(
        'https://api.newrelic.com/graphql',
        headers=HEADERS,
        json={'query': query, 'variables': variables}
    )
    response_data = response.json()
    
    if 'data' in response_data and 'actor' in response_data['data'] and 'entity' in response_data['data']['actor']:
        return response_data['data']['actor']['entity']
    else:
        print(f"Error fetching dashboard JSON for GUID {dashboard_guid}: {response_data}")
        return None

def save_dashboard_json(dashboard_data, file_name):
    try:
        with open(file_name, 'w') as file:
            json.dump(dashboard_data, file, indent=4)
        print(f"Saved dashboard JSON to {file_name}")
    except Exception as e:
        print(f"Error saving dashboard JSON to {file_name}: {e}")

def main():
    dashboards = get_all_dashboards()
    for dashboard in dashboards:
        guid = dashboard['guid']
        name = dashboard['name']
        print(f"Exporting dashboard: {name} (GUID: {guid})")
        
        # Fetch and save the JSON data
        dashboard_data = get_dashboard_json(guid)
        if dashboard_data:
            # Sanitize the file name to avoid issues with special characters
            sanitized_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            json_file_name = f"{sanitized_name}.json"
            save_dashboard_json(dashboard_data, json_file_name)

if __name__ == "__main__":
    main()
