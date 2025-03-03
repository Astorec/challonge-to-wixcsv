import mysql


class player:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    def create_player(self, name, username, region):
        try:
            # if the username is not none, check if it already exists
            if username:
                self.cursor.execute(
                    "SELECT * FROM tblPlayers WHERE username=%s",
                    (username,)
                )
                result = self.cursor.fetchone()
                # if the results are not empty, return the current data
                if result:
                    return result
            
            # If player doesn't exist, create a new player
            self.cursor.execute(
                "SELECT id FROM tblRegions WHERE region=%s",                                
                (region,)
            )

            region_id = self.cursor.fetchone()[0]

            self.cursor.execute(
                "INSERT INTO tblPlayers (name, username, region) VALUES (%s, %s, %s)",
                (name, username,region_id)
            )            
            self.db.commit()

            # If username is none, set query to get the player by name
            if not username:
                self.cursor.execute(
                    "SELECT * FROM tblPlayers WHERE name=%s",
                    (name,)
                )
                return self.cursor.fetchone()
            
            
            # return the newly created player
            self.cursor.execute(
                "SELECT * FROM tblPlayers WHERE name=%s AND username=%s",
                (name, username,)
            )
            result = self.cursor.fetchone()
            print(f"Create player result: {result}")  # Debugging statement
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
    
    def get_player_by_username(self, username):
        self.cursor.execute(
            "SELECT * FROM tblPlayers WHERE username=%s",
            (username,)
        )
        return self.cursor.fetchone()
    
    def get_player_by_name(self, name):
        self.cursor.execute(
            "SELECT * FROM tblPlayers WHERE name=%s",
            (name,)
        )
        return self.cursor.fetchone()
    
    def get_player_by_id(self, player_id):
        self.cursor.execute(
            "SELECT * FROM tblPlayers WHERE id=%s",
            (player_id,)
        )
        return self.cursor.fetchone()