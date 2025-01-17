import os
import json
import time
import challonge
import names


conifg = None
        # Check if config/config.json exists
if os.path.exists('config/config.json'):
    with open('config/config.json') as f:
        config = json.load(f)
else:
    print("Config file not found")
    exit(1)
    
    
def get_matches(tournament_id):
    challonge.set_credentials(config['challonge_api']['username'], config['challonge_api']['key'])
    print("Getting matches for tournament: " + tournament_id)
    matches = challonge.matches.index(tournament_id)
    return matches

def update_matches(tournament_id, matches):
    all_matches_complete = False
    print("Updating matches for tournament: " + tournament_id)
    while not all_matches_complete:
        all_matches_complete = True
        for match in matches:
            print("Match: " + str(match))
            # Check to see if the state is complete
            if match['state'] != 'complete':
                all_matches_complete = False
                # Update the match with the winner
                if match['state'] == 'open':
                    params = {
                    "winner_id": match['player1_id']
                    }
                    challonge.matches.update(tournament_id, match['id'], scores_csv='1-0', **params)
        
        if not all_matches_complete:
            print("Not all matches are complete")
            # Wait for a short period before checking the matches again
            time.sleep(5)
            # Fetch the updated list of matches
            matches = challonge.matches.index(tournament_id)
            
update_matches("test_tournament_for_challonge_to_wix_project_top_8", get_matches("test_tournament_for_challonge_to_wix_project_top_8"))