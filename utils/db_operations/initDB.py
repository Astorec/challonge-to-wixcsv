import mysql.connector
from mysql.connector import errorcode
import json

class initDB:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.connection = None
        self.cursor = None
        self.connect()
        self.init_db()

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.config['db']['host'],
            user=self.config['db']['user'],
            password=self.config['db']['pass'],
            database=self.config['db']['db']
        )
        self.cursor = self.connection.cursor()
        print("DB_HOST", self.config['db']['host'])

    def init_db(self):
        tables = {
            'tblPlayers': (
                "CREATE TABLE IF NOT EXISTS tblPlayers ("
                "  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                "  name VARCHAR(255) NOT NULL,"
                "  username VARCHAR(255) NULL UNIQUE"
                ")"
            ),
            'tblTournamentData': (
                "CREATE TABLE IF NOT EXISTS tblTournamentData ("
                "  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                "  tournament_id INT NOT NULL,"
                "  player_db_id INT NOT NULL,"
                "  wins INT NOT NULL DEFAULT 0,"
                "  losses INT NOT NULL DEFAULT 0,"
                "  `rank` INT NOT NULL DEFAULT 0,"
                "  win_percentage DECIMAL(5, 2) NOT NULL DEFAULT 0,"
                "  first_place INT NOT NULL DEFAULT 0,"
                "  second_place INT NOT NULL DEFAULT 0,"
                "  third_place INT NOT NULL DEFAULT 0,"
                "  fourth_place INT NOT NULL DEFAULT 0,"
                "  fifth_place INT NOT NULL DEFAULT 0,"
                "  sixth_place INT NOT NULL DEFAULT 0,"
                "  seventh_place INT NOT NULL DEFAULT 0,"
                "  eighth_place INT NOT NULL DEFAULT 0,"
                "  FOREIGN KEY (tournament_id) REFERENCES tblTournaments(id),"
                "  FOREIGN KEY (player_db_id) REFERENCES tblPlayers(id)"
                ")"
            ),
            'tblTournaments': (
                "CREATE TABLE IF NOT EXISTS tblTournaments ("
                "  id INT AUTO_INCREMENT PRIMARY KEY,"
                "  name VARCHAR(255) NOT NULL,"
                "  participants INT NULL,"
                "  is_side_event BOOLEAN NULL DEFAULT 0,"
                "  state VARCHAR(255) NOT NULL DEFAULT 'upcoming'"
                ")"
            ),
            'tblParticipants': (
                "CREATE TABLE IF NOT EXISTS tblParticipants ("
                "  id INT AUTO_INCREMENT PRIMARY KEY,"
                "  player_db_id INT NOT NULL,"
                "  tournament_id INT NOT NULL,"
                "  player_id INT NOT NULL,"
                "  group_id INT NULL,"
                "  FOREIGN KEY (player_db_id) REFERENCES tblPlayers(id),"
                "  FOREIGN KEY (tournament_id) REFERENCES tblTournaments(id)"
                ")"
            ),
            'tblMatches': (
                "CREATE TABLE IF NOT EXISTS tblMatches ("
                "  id INT AUTO_INCREMENT PRIMARY KEY,"
                "  player1_id INT NULL,"
                "  player2_id INT NULL,"
                "  winner_id INT NULL,"
                "  loser_id INT NULL,"
                "  tournament_id INT NOT NULL,"
                "  FOREIGN KEY (tournament_id) REFERENCES tblTournaments(id)"
                ")"
            )
        }

        for table_name, create_table_query in tables.items():
            try:
                self.cursor.execute(create_table_query)
                print(f"{table_name} table created successfully")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print(f"Table {table_name} already exists.")
                else:
                    print(f"Error creating table {table_name}: {err.msg}")

    def get_connection(self):
        return self.connection