class participants:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
        
        
    def create_participant(self, tournament_id,  player_db_id, player_id, group_id=None):
        # Check if the participant already exists for the tournament
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        result = self.cursor.fetchone()
        # if the results are not empty, return the current data
        if result:
            return result
        
        # If participant doesn't exist, create a new participant
        self.cursor.execute(
            "INSERT INTO tblParticipants (tournament_id, player_db_id, player_id, group_id) VALUES (%s, %s, %s, %s)",
            (tournament_id, player_db_id, player_id, group_id)
        )
        
        self.db.commit()
        
        # return the newly created participant
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def get_participant_by_player_db_id_tournament_id(self, player_db_id, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE player_db_id=%s AND tournament_id=%s",
            (player_db_id, tournament_id)
        )
        return self.cursor.fetchone()
    
    def get_participant_by_player_id_tournament_id(self, player_id, tournament_id):
        # Get the participant by comparing player_id to player_id or group_id
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE (player_id=%s OR group_id=%s) AND tournament_id=%s",
            (player_id, player_id,tournament_id)
        )
                # Print results for debugging
        results = self.cursor.fetchall()
        print(f"Get Participant by player_id results: {results}")
        
        return results
    
    def get_participant_by_group_id_tournament_id(self, group_id, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE group_id=%s AND tournament_id=%s",
            (group_id, tournament_id)
        )

        result = self.cursor.fetchone()
        print(f"Get Participant by group_id results: {result}")
        return result
    
    def get_participant_by_id_tournament_id(self, participant_id, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE player_id=%s AND tournament_id=%s",
            (participant_id, tournament_id)
        )
        return self.cursor.fetchone()

    def get_participants_by_tournament_id(self, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE tournament_id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
    def remove_participant(self, player_db_id, tournament_id):
        self.cursor.execute(
            "DELETE FROM tblParticipants WHERE player_db_id=%s AND tournament_id=%s",
            (player_db_id, tournament_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblParticipants WHERE player_db_id=%s AND tournament_id=%s",
            (player_db_id, tournament_id)
        )
        return self.cursor.fetchone()