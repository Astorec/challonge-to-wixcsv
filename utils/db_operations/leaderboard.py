
import decimal


class leaderboard:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    
    def get_main_board(self):
        # Query to get the tournament data with player count
        query = """
        SELECT 
            td.player_db_id,
            p.username,
            t.participants,
            td.wins,
            td.first_place,
            td.second_place,
            td.third_place,
            td.fourth_place,
            td.fifth_place,
            td.sixth_place,
            td.seventh_place,
            td.eighth_place,
            td.ninth_place,
            td.tenth_place,
            td.eleventh_place,
            td.twelfth_place,
            td.thirteenth_place,
            td.fourteenth_place,
            td.fifteenth_place,
            td.sixteenth_place
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        JOIN 
            tblTournaments t ON td.tournament_id = t.id
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        # Calculate total points based on the number of participants
        player_points = {}
        for row in results:
            player_db_id = row[0]
            username = row[1] if row[1] is not None else row[2]
            participants_count = row[2]
            wins = row[3]
            first_place = row[4]
            second_place = row[5]
            third_place = row[6]
            fourth_place = row[7]
            fifth_place = row[8]
            sixth_place = row[9]
            seventh_place = row[10]
            eighth_place = row[11]
            ninth_place = row[12]
            tenth_place = row[13]
            eleventh_place = row[14]
            twelfth_place = row[15]
            thirteenth_place = row[16]
            fourteenth_place = row[17]
            fifteenth_place = row[18]
            sixteenth_place = row[19]
            
            # Determine points based on participants count
            points = wins
            if participants_count >= 4 and participants_count <= 8:
                points += first_place * 5
            elif participants_count >= 9 and participants_count <= 16:
                points += first_place * 5 + second_place * 4
            elif participants_count >= 17 and participants_count <= 32:
                points += first_place * 5 + second_place * 4 + third_place * 3 + fourth_place * 2
            elif participants_count >= 33 and participants_count <= 64:
                points += first_place * 5 + second_place * 4 + third_place * 3 + fourth_place * 2 + fifth_place * 1 + sixth_place * 1 + seventh_place * 1 + eighth_place * 1
            elif participants_count >= 65:
                points += first_place * 10 + second_place * 9 + third_place * 8 + fourth_place * 7 + fifth_place * 6 + sixth_place * 5 + seventh_place * 4 + eighth_place * 3 + ninth_place * 1 + tenth_place * 1 + eleventh_place * 1 + twelfth_place * 1 + thirteenth_place * 1 + fourteenth_place * 1 + fifteenth_place * 1 + sixteenth_place * 1
            
            if player_db_id not in player_points:
                player_points[player_db_id] = {"username": username, "total_points": 0}
            player_points[player_db_id]["total_points"] += points
        
        # Sort players by total points
        sorted_players = sorted(player_points.items(), key=lambda x: x[1]["total_points"], reverse=True)
        
        # Update rank for each player
        ranked_results = []
        rank = 1
        for player in sorted_players:
            player_db_id = player[0]
            username = player[1]["username"]
            total_points = player[1]["total_points"]
            update_query = """
            UPDATE tblTournamentData
            SET `rank` = %s
            WHERE player_db_id = %s;
            """
            self.cursor.execute(update_query, (rank, player_db_id))
            
            
            ranked_results.append((rank, username, total_points))
            rank += 1
        
        self.db.commit()
        
        return ranked_results
    def get_tournament_leaderboard(self, tournament_id):
        # Query to get the tournament data with player count for a specific tournament
        query = """
        SELECT 
            td.player_db_id,
            p.username,
            p.name,
            t.participants,
            td.wins,
            td.first_place,
            td.second_place,
            td.third_place,
            td.fourth_place,
            td.fifth_place,
            td.sixth_place,
            td.seventh_place,
            td.eighth_place,
            td.ninth_place,
            td.tenth_place,
            td.eleventh_place,
            td.twelfth_place,
            td.thirteenth_place,
            td.fourteenth_place,
            td.fifteenth_place,
            td.sixteenth_place
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        JOIN 
            tblTournaments t ON td.tournament_id = t.id
        WHERE 
            td.tournament_id = %s
        """
        
        self.cursor.execute(query, (tournament_id,))
        results = self.cursor.fetchall()
        
        # Calculate total points based on the number of participants
        player_points = {}
        for row in results:
            player_db_id = row[0]
            username = row[1] if row[1] is not None else row[2]  # Use name if username is null
            participants_count = row[3]
            wins = row[4]
            first_place = row[5]
            second_place = row[6]
            third_place = row[7]
            fourth_place = row[8]
            fifth_place = row[9]
            sixth_place = row[10]
            seventh_place = row[11]
            eighth_place = row[12]
            ninth_place = row[13]
            tenth_place = row[14]
            eleventh_place = row[15]
            twelfth_place = row[16]
            thirteenth_place = row[17]
            fourteenth_place = row[18]
            fifteenth_place = row[19]
            sixteenth_place = row[20]
            
            # Determine points based on participants count
            points = wins
            if participants_count >= 4 and participants_count <= 8:
                points += first_place * 5
            elif participants_count >= 9 and participants_count <= 16:
                points += first_place * 5 + second_place * 4
            elif participants_count >= 17 and participants_count <= 32:
                points += first_place * 5 + second_place * 4 + third_place * 3 + fourth_place * 2
            elif participants_count >= 33 and participants_count <= 64:
                points += first_place * 5 + second_place * 4 + third_place * 3 + fourth_place * 2 + fifth_place * 1 + sixth_place * 1 + seventh_place * 1 + eighth_place * 1
            elif participants_count >= 65:
                points += first_place * 10 + second_place * 9 + third_place * 8 + fourth_place * 7 + fifth_place * 6 + sixth_place * 5 + seventh_place * 4 + eighth_place * 3 + ninth_place * 1 + tenth_place * 1 + eleventh_place * 1 + twelfth_place * 1 + thirteenth_place * 1 + fourteenth_place * 1 + fifteenth_place * 1 + sixteenth_place * 1
            
            if player_db_id not in player_points:
                player_points[player_db_id] = {"username": username, "total_points": 0}
            player_points[player_db_id]["total_points"] += points
        
        # Sort players by total points
        sorted_players = sorted(player_points.items(), key=lambda x: x[1]["total_points"], reverse=True)
        
        # Prepare ranked results
        ranked_results = []
        rank = 1
        for player in sorted_players:
            player_db_id = player[0]
            username = player[1]["username"]
            total_points = player[1]["total_points"]
            ranked_results.append((rank, username, total_points))
            rank += 1
        
        return ranked_results
    
    def get_region_leaderboard(self, region):
        # Query to get the tournament data with player count for a specific region
        query = """
        SELECT 
            td.player_db_id,
            p.username,
            p.name,
            t.participants,
            td.wins,
            td.first_place,
            td.second_place,
            td.third_place,
            td.fourth_place,
            td.fifth_place,
            td.sixth_place,
            td.seventh_place,
            td.eighth_place,
            td.ninth_place,
            td.tenth_place,
            td.eleventh_place,
            td.twelfth_place,
            td.thirteenth_place,
            td.fourteenth_place,
            td.fifteenth_place,
            td.sixteenth_place
        FROM 
            tblTournamentData td
        JOIN 
            tblPlayers p ON td.player_db_id = p.id
        JOIN 
            tblTournaments t ON td.tournament_id = t.id
        JOIN 
            tblRegions r ON t.region = r.id
        WHERE 
            r.id = %s
        """
        
        self.cursor.execute(query, (region,))
        results = self.cursor.fetchall()
        
        # Calculate total points based on the number of participants
        player_points = {}
        for row in results:
            player_db_id = row[0]
            username = row[1] if row[1] is not None else row[2]  # Use name if username is null
            participants_count = row[3]
            wins = row[4]
            first_place = row[5]
            second_place = row[6]
            third_place = row[7]
            fourth_place = row[8]
            fifth_place = row[9]
            sixth_place = row[10]
            seventh_place = row[11]
            eighth_place = row[12]
            ninth_place = row[13]
            tenth_place = row[14]
            eleventh_place = row[15]
            twelfth_place = row[16]
            thirteenth_place = row[17]
            fourteenth_place = row[18]
            fifteenth_place = row[19]
            sixteenth_place = row[20]
            
            # Determine points based on participants count
            points = wins
            if participants_count >= 4 and participants_count <= 8:
                points += first_place * 5
            elif participants_count >= 9 and participants_count <= 16:
                points += first_place * 5 + second_place * 4
            elif participants_count >= 17 and participants_count <= 32:
                points += first_place * 5 + second_place * 4 + third_place * 3 + fourth_place * 2
            elif participants_count >= 33 and participants_count <= 64:
                points += first_place * 5 + second_place * 4 + third_place * 3 + fourth_place * 2 + fifth_place * 1 + sixth_place * 1 + seventh_place * 1 + eighth_place * 1
            elif participants_count >= 65:
                points += first_place * 10 + second_place * 9 + third_place * 8 + fourth_place * 7 + fifth_place * 6 + sixth_place * 5 + seventh_place * 4 + eighth_place * 3 + ninth_place * 1 + tenth_place * 1 + eleventh_place * 1 + twelfth_place * 1 + thirteenth_place * 1 + fourteenth_place * 1 + fifteenth_place * 1 + sixteenth_place * 1
            
            if player_db_id not in player_points:
                player_points[player_db_id] = {"username": username, "total_points": 0}
            player_points[player_db_id]["total_points"] += points
        
        # Sort players by total points
        sorted_players = sorted(player_points.items(), key=lambda x: x[1]["total_points"], reverse=True)
        
        # Prepare ranked results
        ranked_results = []
        rank = 1
        for player in sorted_players:
            player_db_id = player[0]
            username = player[1]["username"]
            total_points = player[1]["total_points"]
            ranked_results.append((rank, username, total_points))
            rank += 1
        
        return ranked_results