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
    tournament = challonge.tournaments.show("1savs9wo")
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
    
    
    challonge.participants.bulk_add(tournament['url'], participants)

create_challonge_tournament()
create_challonge_participants(32)

# Print the tournament URL returned from Challonge
print(tournament['url'])
