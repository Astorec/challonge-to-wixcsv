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
    
    def add_placement(self, tournament_id, player_db_id, placement, is_store_championship = True):        
        
        self.cursor.execute(
        f"UPDATE tblTournamentData SET`rank`=%s WHERE tournament_id=%s AND player_db_id=%s",
        (placement, tournament_id, player_db_id)
        )
            
        self.db.commit()

        if not is_store_championship and placement <=16:
            self.update_score_for_top_cut(tournament_id, player_db_id, is_store_championship)
    
    def get_top_cut_size(self, touranment_id):
        self.cursor.execute(
            "SELECT top_cut FROM tblTournamentAttendance WHERE id=(SELECT attendance_id FROM tblTournaments WHERE id=%s)",
            (touranment_id,)
        )
        return self.cursor.fetchone()[0]

    def update_score_for_top_cut(self, tournament_id, player_db_id, is_store_championship):
        # Get the attendance_id from tblTournaments where the tournament_id is the one we're looking for
        # and get the top_cut from tblTournamentAttendance where the attendance_id is the one we just got
        self.cursor.execute(
        "SELECT attendance_id FROM tblTournaments WHERE id=%s",
        (tournament_id,)
        )
        attendance_id = self.cursor.fetchone()[0]
        
        self.cursor.execute(
            "SELECT top_cut FROM tblTournamentAttendance WHERE id=%s",
            (attendance_id,)
        )
        
        top_cut = self.cursor.fetchone()[0]
        
        # Figure out score modifiers based on top_cut. Example for top 16:
        # 1st to 16th 10/9/8/7/6/5/4/3
        #             1/1/1/1/1/1/1/1/1
        # For Top 8: 1st to 8th 5/4/3/2/1/1/1/1
        # For Top 4: 1st to 4th 5/4/3/2
        # For Top 2: 1st to 2nd 5/4
        # For Top 1: 1st 5
        
        score_modifiers = []

        if is_store_championship:
            if top_cut == 16:
                score_modifiers = [10, 9, 8, 7, 6, 5, 4, 3, 1, 1, 1, 1, 1, 1, 1, 1]
            elif top_cut == 8:
                score_modifiers = [5, 4, 3, 2, 1, 1, 1, 1]
            elif top_cut == 4:
                score_modifiers = [5, 4, 3, 2]
            elif top_cut == 2:
                score_modifiers = [5, 4, 0, 0]
            elif top_cut == 1:
                score_modifiers = [5, 0, 0, 0]
            else:
                print(f"Unknown top cut: {top_cut}")
                return
        else:
             score_modifiers = [10, 10, 10, 10, 6, 6, 6, 6, 4, 4, 4, 4, 4, 4, 4, 4]
        
        
        self.cursor.execute(
            "SELECT `rank` FROM tblTournamentData WHERE tournament_id=%s AND player_db_id=%s",
            (tournament_id, player_db_id)
        )
        
        placement = self.cursor.fetchone()[0]
        
        self.cursor.execute(
            "UPDATE tblTournamentData SET score=%s WHERE tournament_id=%s AND player_db_id=%s",
            (score_modifiers[placement - 1], tournament_id, player_db_id)
        )
        self.db.commit()
    
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