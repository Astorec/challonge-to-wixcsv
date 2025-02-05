class matches:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
        
    def add_match(self, match_id, player1_id, player2_id, tournament_id):
        # check if match already exists
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE match_id=%s AND player1_id=%s AND player2_id=%s AND tournament_id=%s",
            (match_id, player1_id, player2_id, tournament_id)
        )
        
        result = self.cursor.fetchone()
        if result:
            return result
        
        self.cursor.execute(
            "INSERT INTO tblMatches (match_id, player1_id, player2_id, tournament_id) VALUES (%s,%s, %s, %s)",
            (match_id, player1_id, player2_id, tournament_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE match_id=%s AND player1_id=%s AND player2_id=%s AND tournament_id=%s",
            (match_id, player1_id, player2_id, tournament_id)
        )
        return self.cursor.fetchone()
    
    def get_matches_by_tournament_id(self, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE tournament_id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
    def set_match_to_final(self, match_id):
        self.cursor.execute(
            "UPDATE tblMatches SET is_finals=1 WHERE match_id=%s",
            (match_id,)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE match_id=%s",
            (match_id,)
        )
        return self.cursor.fetchone()
    
    def get_matches_for_finals(self, tournament_id, match_id):
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE tournament_id=%s AND id=%s AND is_finals=1",
            (tournament_id, match_id)
        )
        return self.cursor.fetchone()
    
    def get_player_finals_matches(self,player_id):
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE winner_id=%s or loser_id=%s AND is_finals=1",
            (player_id,player_id)
        )
        
        # Return list of matches
        return self.cursor.fetchall()
    
    def get_finals_matches(self, tournament_id):
        query = """
        SELECT m.*
        FROM tblMatches m
        JOIN tblParticipants p1 ON m.player1_id = p1.player_id
        JOIN tblParticipants p2 ON m.player2_id = p2.player_id
        WHERE m.tournament_id = %s AND m.is_finals = 1 AND p1.tournament_id = %s AND p2.tournament_id = %s
        """
        self.cursor.execute(query, (tournament_id, tournament_id, tournament_id))
        return self.cursor.fetchall()
    
    def get_match_by_id(self, match_id):
      
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE match_id=%s",
            (match_id,)
        )
        return self.cursor.fetchone()
    
    def get_match_by_players(self, player1_id, player2_id, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE player1_id=%s AND player2_id=%s AND tournament_id=%s",
            (player1_id, player2_id, tournament_id)
        )
        return self.cursor.fetchone()
    def update_match_winner(self, match_id, winner_id, loser_id):
        self.cursor.execute(
            "UPDATE tblMatches SET winner_id=%s, loser_id=%s WHERE id=%s",
            (winner_id, loser_id, match_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE id=%s",
            (match_id,)
        )
        return self.cursor.fetchone()
    
    def undo_match_winner(self, match_id):
        self.cursor.execute(
            "UPDATE tblMatches SET winner_id=NULL, loser_id=NULL WHERE id=%s",
            (match_id,)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblMatches WHERE id=%s",
            (match_id,)
        )
        return self.cursor.fetchone()
    
    def get_match_winner(self, match_id):
        self.cursor.execute(
            "SELECT winner_id FROM tblMatches WHERE id=%s",
            (match_id,)
        )
        return self.cursor.fetchone()
    