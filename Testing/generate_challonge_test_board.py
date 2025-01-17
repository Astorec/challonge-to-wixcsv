import os
import json
import challonge
import names

tournament = None
participants = []

conifg = None
        # Check if config/config.json exists
if os.path.exists('config/config.json'):
    with open('config/config.json') as f:
        config = json.load(f)
else:
    print("Config file not found")
    exit(1)
    

def create_challonge_tournament():
    challonge.set_credentials(config['challonge_api']['username'], config['challonge_api']['key'])
    tournament = challonge.tournaments.create(
        "Test Tournament For Challonge To Wix Project Top 8",
        "test_tournament_for_challonge_to_wix_project_Top_8",
        "double elimination"
    )
    return tournament

def create_challonge_participants(participant_count):
    # Create Random Participants for testing up to passed in number
    
    # Generate random names for participants and add those names to the list
    for i in range(participant_count):
        name = names.get_full_name()
        # Check if the name is already in the list
        while name in participants:
            name = names.get_full_name()            
        participants.append(name)
    
    
    challonge.participants.bulk_add(tournament['id'], participants)
    
tournament = create_challonge_tournament()
create_challonge_participants(32)

# Print the tournament URL returned from Challonge
print(tournament['url'])
