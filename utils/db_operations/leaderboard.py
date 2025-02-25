class leaderboard:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    
    def get_main_board(self):
        # Query to get the tournament data with player count
        query = """
SELECT
		ROW_NUMBER() OVER (ORDER BY SUM(td.score) DESC) AS player_rank,
        COALESCE(p.username, p.name) AS display_name,
        SUM(td.score) AS total_score,        
        ROUND(
          CASE
          WHEN SUM(td.wins) + SUM(td.losses) = 0 THEN 0.0
          ELSE (SUM(td.wins) * 100.0) / (SUM(td.wins) + SUM(td.losses))
          END
          ) AS total_win_percentage,
        r.region
        FROM
            tblTournamentData td
        JOIN
            tblPlayers p ON td.player_db_id = p.id
        JOIN
            tblTournaments t ON td.tournament_id = t.id
        JOIN
            tblRegions r ON p.region = r.id
        GROUP BY
            p.name,
            p.username,
            r.region
        ORDER BY
            player_rank
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        return results            
        
    def get_tournament_leaderboard(self, tournament_id):
        # Query to get the tournament data with player count for a specific tournament
        query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(td.score) DESC) AS player_rank,
            COALESCE(p.username, p.name) AS display_name,    
            td.score,
                    ROUND(
          CASE
          WHEN SUM(td.wins) + SUM(td.losses) = 0 THEN 0.0
          ELSE (SUM(td.wins) * 100.0) / (SUM(td.wins) + SUM(td.losses))
          END
          ) AS win_percentage,
            r.region
        FROM
            tblTournamentData td
        JOIN
            tblPlayers p ON td.player_db_id = p.id
        JOIN
                tblTournaments t on td.tournament_id = t.id
        JOIN
            tblRegions r ON p.region = r.id
        WHERE
            td.tournament_id = %s
        GROUP BY 
            td.rank,
            p.username,
            p.name,
            td.score,
            r.region
        ORDER BY
                td.rank ASC
        """        
        self.cursor.execute(query, (tournament_id,))
        results = self.cursor.fetchall()
        
        return results
    
    def get_region_leaderboard(self, region):
        # Query to get the tournament data with player count for a specific region
        query = """
      SELECT
		ROW_NUMBER() OVER (ORDER BY SUM(td.score) DESC) AS player_rank,
        COALESCE(p.username, p.name) AS display_name,
        SUM(td.score) AS total_score,
                ROUND(
          CASE
          WHEN SUM(td.wins) + SUM(td.losses) = 0 THEN 0.0
          ELSE (SUM(td.wins) * 100.0) / (SUM(td.wins) + SUM(td.losses))
          END
          ) AS total_win_percentage,
        r.region
    FROM
        tblTournamentData td
    JOIN
        tblPlayers p ON td.player_db_id = p.id
    JOIN
        tblTournaments t ON td.tournament_id = t.id
    JOIN
        tblRegions r ON p.region = r.id
    WHERE
        t.region = %s
    GROUP BY
        p.name,
        p.username,
        r.region
    ORDER BY
        player_rank
        """
        
        self.cursor.execute(query, (region,))
        results = self.cursor.fetchall()
        
        return results