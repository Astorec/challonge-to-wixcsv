import os
import json
import time
import challonge

conifg = None
        # Check if config/config.json exists
if os.path.exists('config/config.json'):
    with open('config/config.json') as f:
        config = json.load(f)
else:
    print("Config file not found")
    exit(1)
    

def reset():
    challonge.set_credentials(config['challonge_api']['username'], config['challonge_api']['key'])
    
    params = {
        "include_matches": 1,
        "include_participants": 0
    }
    challonge.tournaments.reset("test_tournament_for_challonge_to_wix_project_top_8", **params)
    
reset()