import challonge

class calls:
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key        
        challonge.set_credentials(self.username, self.api_key)
        
    def get_tournament(self, tournament_id):
        return challonge.tournaments.show(tournament_id)
    
    def get_participants(self, tournament_id):
        return challonge.participants.index(tournament_id)#
    
    def get_matches(self, tournament_id):
        return challonge.matches.index(tournament_id) 
    
    def get_match(self, tournament_id, match_id):
        return challonge.matches.show(tournament_id, match_id)

