import decimal
class tournamentData:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
        
    def add_data(self, tournament_id, player_db_id):
        self.cursor.execute(
            "INSERT INTO tblTournamentData (tournament_id, player_db_id) VALUES (%s, %s)",
            (tournament_id, player_db_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def get_data(self, tournament_id, player_db_id):
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def add_win(self, tournament_id, player_db_id):
        self.cursor.execute(
            "UPDATE tblTournamentData SET wins=wins+1 WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def add_loss(self, tournament_id, player_db_id):
        self.cursor.execute(
            "UPDATE tblTournamentData SET losses=losses+1 WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def remove_win(self, tournament_id, player_db_id):
        self.cursor.execute(
            "UPDATE tblTournamentData SET wins=wins-1 WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def remove_loss(self, tournament_id, player_db_id):
        self.cursor.execute(
            "UPDATE tblTournamentData SET losses=losses-1 WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def add_placement(self, tournament_id, player_db_id, placement):
        
        if placement == 1:
            placement = "first_place"
        elif placement == 2:
            placement = "second_place"
        elif placement == 3:
            placement = "third_place"
        elif placement == 4:
            placement = "fourth_place"
        elif placement == 5:
            placement = "fifth_place"
        elif placement == 6:
            placement = "sixth_place"
        elif placement == 7:
            placement = "seventh_place"
        elif placement == 8:
            placement = "eighth_place"
        
        self.cursor.execute(
            f"UPDATE tblTournamentData SET {placement}={placement}+1 WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def sort_data_by_score_add_rank(self):
        # Query to calculate points and sort players
        query = """
        SELECT 
            td.player_db_id,
            (SUM(td.wins) + 
            SUM(td.first_place) * 5 + 
            SUM(td.second_place) * 4 + 
            SUM(td.third_place) * 3 + 
            SUM(td.fourth_place) * 2 + 
            SUM(td.fifth_place) * 1 + 
            SUM(td.sixth_place) * 1 + 
            SUM(td.seventh_place) * 1 + 
            SUM(td.eighth_place) * 1) AS total_points
        FROM 
            tblTournamentData td
        GROUP BY 
            td.player_db_id
        ORDER BY 
            total_points DESC;
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        ranked_results = []
        # Update rank for each player
        rank = 1
        for row in results:
            player_db_id = row[0]
            update_query = """
            UPDATE tblTournamentData
            SET `rank` = %s
            WHERE player_db_id = %s;
            """
            self.cursor.execute(update_query, (rank, player_db_id))
            rank += 1
        
        self.db.commit()
        
        self.cursor.execute(
            """        SELECT 
            td.rank, 
            p.username, 
            (SUM(td.wins) + 
            SUM(td.first_place) * 5 + 
            SUM(td.second_place) * 4 + 
            SUM(td.third_place) * 3 + 
            SUM(td.fourth_place) * 2 + 
            SUM(td.fifth_place) * 1 + 
            SUM(td.sixth_place) * 1 + 
            SUM(td.seventh_place) * 1 + 
            SUM(td.eighth_place) * 1) AS total_points 
        FROM 
            tblTournamentData td 
        JOIN 
            tblPlayers p ON td.player_db_id = p.id 
        GROUP BY 
            td.rank, p.username 
        ORDER BY 
            total_points DESC"""
        )
        updated_results = self.cursor.fetchall()
        
        # Convert Decimal to float for total_points in updated results
        final_results = []
        for row in updated_results:
            total_points = float(row[2]) if isinstance(row[2], decimal.Decimal) else row[2]
            final_results.append((row[0], row[1], total_points))
        
        return final_results