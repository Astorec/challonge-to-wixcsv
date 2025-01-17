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
    
    def get_tournament_data(self, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
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
        placement_column = ""
        if placement == 1:
            placement_column = "first_place"
        elif placement == 2:
            placement_column = "second_place"
        elif placement == 3:
            placement_column = "third_place"
        elif placement == 4:
            placement_column = "fourth_place"
        elif placement == 5:
            placement_column = "fifth_place"
        elif placement == 6:
            placement_column = "sixth_place"
        elif placement == 7:
            placement_column = "seventh_place"
        elif placement == 8:
            placement_column = "eighth_place"
        elif placement == 9:
            placement_column = "ninth_place"
        elif placement == 10:
            placement_column = "tenth_place"
        elif placement == 11:
            placement_column = "eleventh_place"
        elif placement == 12:
            placement_column = "twelfth_place"
        elif placement == 13:
            placement_column = "thirteenth_place"
        elif placement == 14:
            placement_column = "fourteenth_place"
        elif placement == 15:
            placement_column = "fifteenth_place"
        elif placement == 16:
            placement_column = "sixteenth_place"
        
        
        if placement_column == "":
               self.cursor.execute(
            f"UPDATE tblTournamentData SET`rank`=%s WHERE tournament_id=%s AND player_db_id=%s",
            (placement, tournament_id, player_db_id)
        )
        else:                        
            self.cursor.execute(
                f"UPDATE tblTournamentData SET {placement_column}={placement_column}+1, `rank`=%s WHERE tournament_id=%s AND player_db_id=%s",
                (placement, tournament_id, player_db_id)
            )
            
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        return self.cursor.fetchone()
    
    def update_win_percentage(self, tournament_id, player_db_id):
        self.cursor.execute(
            "SELECT wins, losses FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        result = self.cursor.fetchone()
        
        if result is None:
            print(f"No data found for tournament_id={tournament_id} and player_db_id={player_db_id}")
            return
        
        wins, losses = result
        
        if wins + losses == 0:
            win_percentage = decimal.Decimal(0)
        else:
            win_percentage = decimal.Decimal(wins) / decimal.Decimal(wins + losses)
        
        self.cursor.execute(
            "UPDATE tblTournamentData SET win_percentage=%s WHERE tournament_id=%s AND player_db_id=%s",
            (win_percentage, tournament_id, player_db_id)
        )
        self.db.commit()
   
    def get_top_cut(self, tournament_id, placement):
        # Sort by rank and get amount based on placement
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s ORDER BY `rank` ASC LIMIT %s",
            (tournament_id, placement)
        )
        return self.cursor.fetchall()

    def get_all_players_with_scores(self, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblTournamentData WHERE tournament_id=%s ORDER BY `rank` ASC",
            (tournament_id,)
        )
        return self.cursor.fetchall()