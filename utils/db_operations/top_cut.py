class top_cut:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
        
    def get_top_one(self, tournament_id):
        self.cursor.execute(
            """SELECT 
            p.name,
            p.username
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        WHERE
            td.tournament_id = %s
        GROUP BY 
            p.name, p.username
        ORDER BY 
            (SUM(td.wins) + 
            SUM(td.first_place) * 5) DESC
        LIMIT 1;"""
            (tournament_id,)
        )
        return self.cursor.fetchone()
        
    def get_top_two(self, tournament_id):
        self.cursor.execute(
            """SELECT 
            p.name,
            p.username
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        WHERE
            td.tournament_id = %s
        GROUP BY 
            p.name, p.username
        ORDER BY 
            (SUM(td.wins) + 
            SUM(td.first_place) * 5 + 
            SUM(td.second_place) * 4) DESC
        LIMIT 2;"""
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
    def get_top_four(self, tournament_id):
        self.cursor.execute(
            """SELECT 
            p.name,
            p.username
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        WHERE
            td.tournament_id = %s
        GROUP BY 
            p.name, p.username
        ORDER BY 
            (SUM(td.wins) + 
            SUM(td.first_place) * 5 + 
            SUM(td.second_place) * 4 + 
            SUM(td.third_place) * 3 + 
            SUM(td.fourth_place) * 2) DESC
        LIMIT 4;"""
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
    def get_top_eight(self, tournament_id):
        self.cursor.execute(
            """SELECT 
            p.name,
            p.username
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        WHERE
            td.tournament_id = %s
        GROUP BY 
            p.name, p.username
        ORDER BY 
            (SUM(td.wins) + 
            SUM(td.first_place) * 5 + 
            SUM(td.second_place) * 4 + 
            SUM(td.third_place) * 3 + 
            SUM(td.fourth_place) * 2 + 
            SUM(td.fifth_place) * 1 + 
            SUM(td.sixth_place) * 1 + 
            SUM(td.seventh_place) * 1 + 
            SUM(td.eighth_place) * 1) DESC
        LIMIT 8;"""
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
    def get_top_sixteen(self, tournament_id):
        self.cursor.execute(
            """SELECT 
                p.name,
                p.username,
                (SUM(td.wins) + 
                SUM(td.first_place) * 10 + 
                SUM(td.second_place) * 9 +
                SUM(td.third_place) * 8 + 
                SUM(td.fourth_place) * 7 + 
                SUM(td.fifth_place) * 6 + 
                SUM(td.sixth_place) * 5 + 
                SUM(td.seventh_place) * 4 + 
                SUM(td.eighth_place) * 3 + 
                SUM(td.ninth_place) * 2 + 
                SUM(td.tenth_place) * 1 + 
                SUM(td.eleventh_place) * 1 + 
                SUM(td.twelfth_place) * 1 + 
                SUM(td.thirteenth_place) * 1 + 
                SUM(td.fourteenth_place) * 1 + 
                SUM(td.fifteenth_place) * 1 + 
                SUM(td.sixteenth_place) * 1) AS total_points
            FROM 
                tblTournamentData td
            JOIN 
                tblPlayers p ON td.player_db_id = p.id
            WHERE
                td.tournament_id = %s
            GROUP BY 
                p.name, p.username
            ORDER BY 
                total_points DESC
            LIMIT 16;""",
            (tournament_id,)
        )
        return self.cursor.fetchall()
    
    def get_top_four_specific_players(self, tournament_id, player_ids):

        # Convert the list of player IDs to a tuple
        player_ids_tuple = tuple(player_ids)
        
        # Ensure the tuple is not empty
        if not player_ids_tuple:
            return []

        # Create a string with the correct number of placeholders
        placeholders = ', '.join(['%s'] * len(player_ids_tuple))

        query = f"""
        SELECT 
            p.name,
            p.username,
            (SUM(td.wins) + 
            SUM(td.first_place) * 5 + 
            SUM(td.second_place) * 4 +
            SUM(td.third_place) * 3 + 
            SUM(td.fourth_place) * 2) AS total_points
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        WHERE
            td.tournament_id = %s AND td.player_db_id IN ({placeholders})
        GROUP BY 
            p.name, p.username
        ORDER BY 
            total_points DESC
        LIMIT 4;
        """
        
        self.cursor.execute(query, (tournament_id, *player_ids))
        return self.cursor.fetchall()
    
    def get_top_eight_specific_players(self, tournament_id, player_ids):


        query = f"""
        SELECT 
            m.id AS match_id,
            tp1.player_db_id AS player1_db_id,
            tp2.player_db_id AS player2_db_id,
            p1.name AS player1_name,
            p1.username AS player1_username,
            p2.name AS player2_name,
            p2.username AS player2_username,
            tpw.player_db_id AS winner_db_id,
            pw.name AS winner_name,
            pw.username AS winner_username,
            tpl.player_db_id AS loser_db_id,
            pl.name AS loser_name,
            pl.username AS loser_username
            
        FROM 
            tblMatches m
        JOIN 
            tblParticipants tp1 ON m.player1_id = tp1.player_id
        JOIN 
            tblParticipants tp2 ON m.player2_id = tp2.player_id
        JOIN 
            tblPlayers p1 ON tp1.player_db_id = p1.id
        JOIN 
            tblPlayers p2 ON tp2.player_db_id = p2.id
        JOIN 
            tblParticipants tpw ON m.winner_id = tpw.player_id
        JOIN
                tblParticipants tpl ON m.loser_id = tpl.player_id
        JOIN 
            tblPlayers pw ON tpw.player_db_id = pw.id
        JOIN
                tblPlayers pl ON tpl.player_db_id = pl.id
        WHERE 
            m.tournament_id = %s AND m.is_finals = 1 
        """
    
            
        # Debugging: Print the query and parameters
        print("Executing query:")
        print(query)
        print("With parameters:")
        print((tournament_id))
        
        self.cursor.execute(query, (tournament_id,))
        matches = self.cursor.fetchall()
    
        return matches
        
    def get_top_sixteen_specific_players(self, tournament_id, player_ids):
        # Convert the list of player IDs to a tuple
        player_ids_tuple = tuple(player_ids)
        
        # Ensure the tuple is not empty
        if not player_ids_tuple:
            return []

        # Create a string with the correct number of placeholders
        placeholders = ', '.join(['%s'] * len(player_ids_tuple))

        query = f"""
        SELECT 
            p.name,
            p.username,
            (SUM(td.wins) + 
            SUM(td.first_place) * 10 + 
            SUM(td.second_place) * 9 +
            SUM(td.third_place) * 8 + 
            SUM(td.fourth_place) * 7 +
            sum(td.fifth_place) * 6 +
            sum(td.sixth_place) * 5 +
            sum(td.seventh_place) * 4 +
            sum(td.eighth_place) * 3 +
            sum(td.ninth_place) +
            sum(td.tenth_place) +
            sum(td.eleventh_place) +
            sum(td.twelfth_place) +
            sum(td.thirteenth_place) +
            sum(td.fourteenth_place) +
            sum(td.fifteenth_place) +
            sum(td.sixteenth_place)) AS total_points
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        WHERE
            td.tournament_id = %s AND td.player_db_id IN ({placeholders})
        GROUP BY 
            p.name, p.username
        ORDER BY 
            total_points DESC
        LIMIT 8;
        """
        
        self.cursor.execute(query, (tournament_id, *player_ids))
        return self.cursor.fetchall()