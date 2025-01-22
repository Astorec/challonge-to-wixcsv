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
            password=self.config['db']['pass']
        )
        self.cursor = self.connection.cursor()
        # Create database if it doesn't exist
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['db']['db']}")
        # Use the database
        self.cursor.execute(f"USE {self.config['db']['db']}")
        
        print("DB_HOST", self.config['db']['host'])

    def init_db(self):
        tables = {
            'tblRegions': (
                "CREATE TABLE IF NOT EXISTS tblRegions ("
                " id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                " region VARCHAR(255) NULL,"
                " short VARCHAR(255) NULL"
                ");"
            ),
            'tblTournamentAttendance': (
                "CREATE TABLE IF NOT EXISTS tblTournamentAttendance ("
                " id INT UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                " top_cut INT NULL,"
                " min INT NULL,"
                " max INT NULL"
                ");"
            ),
            'tblTournaments': (
                "CREATE TABLE IF NOT EXISTS tblTournaments ("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " name VARCHAR(255) NOT NULL,"
                " url VARCHAR(255) NOT NULL,"
                " participants INT NULL,"
                " is_side_event BOOLEAN NULL DEFAULT 0,"
                " region INT DEFAULT 14,"
                " attendance_id INT UNSIGNED DEFAULT 6,"
                " finalized TINYINT(1) DEFAULT 0,"
                " state VARCHAR(255) NOT NULL DEFAULT 'upcoming',"
                " FOREIGN KEY (region) REFERENCES tblRegions(id),"
                " FOREIGN KEY (attendance_id) REFERENCES tblTournamentAttendance(id)"
                ");"
            ),
            'tblPlayers': (
                "CREATE TABLE IF NOT EXISTS tblPlayers ("
                " id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                " name VARCHAR(255) NOT NULL,"
                " username VARCHAR(255) NULL UNIQUE,"
                " region INT DEFAULT 14,"
                " FOREIGN KEY (region) REFERENCES tblRegions(id)"
                ");"
            ),
            'tblTournamentData': (
                "CREATE TABLE IF NOT EXISTS tblTournamentData ("
                " id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                " tournament_id INT NOT NULL,"
                " player_db_id INT NOT NULL,"
                " wins INT NOT NULL DEFAULT 0,"
                " losses INT NOT NULL DEFAULT 0,"
                " `rank` INT NOT NULL DEFAULT 0,"
                " win_percentage DECIMAL(5, 2) NOT NULL DEFAULT 0,"
                " score INT UNSIGNED NOT NULL DEFAULT 0,"
                " FOREIGN KEY (tournament_id) REFERENCES tblTournaments(id),"
                " FOREIGN KEY (player_db_id) REFERENCES tblPlayers(id)"
                ");"
            ),
            'tblParticipants': (
                "CREATE TABLE IF NOT EXISTS tblParticipants ("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " player_db_id INT NOT NULL,"
                " tournament_id INT NOT NULL,"
                " player_id INT NOT NULL,"
                " group_id INT NULL,"
                " FOREIGN KEY (player_db_id) REFERENCES tblPlayers(id),"
                " FOREIGN KEY (tournament_id) REFERENCES tblTournaments(id)"
                ");"
            ),
            'tblMatches': (
                "CREATE TABLE IF NOT EXISTS tblMatches ("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " player1_id INT NULL,"
                " player2_id INT NULL,"
                " winner_id INT NULL,"
                " loser_id INT NULL,"
                " tournament_id INT NOT NULL,"
                " is_finals TINYINT(1) DEFAULT 0,"
                " match_id INT NULL,"
                " FOREIGN KEY (tournament_id) REFERENCES tblTournaments(id)"
                ");"
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

         # Insert initial data into tblRegions
        regions = [
            ('Scotland', 'SCOT'),
            ('North East', 'NE'),
            ('North West', 'NW'),
            ('Yorkshire & The Humber', 'YH'),
            ('East Midlands', 'EM'),
            ('West Midlands', 'WM'),
            ('East of England', 'EE'),
            ('London', 'LOND'),
            ('South East', 'SE'),
            ('South West', 'SW'),
            ('Wales', 'WAL'),
            ('Northern Ireland', 'NI'),
            ('Unassigned', 'IRE')
        ]

        try:
            for region, short in regions:
                self.cursor.execute(
                    "INSERT INTO tblRegions (region, short) VALUES (%s, %s)",
                    (region, short)
                )
            self.connection.commit()
            print("Initial data inserted into tblRegions successfully")
        except mysql.connector.Error as err:
            print(f"Error inserting data into tblRegions: {err}")
            
        # Insert initial data into tblTournamentAttendance
        attendance = [
            (1, 4, 8),
            (2, 9, 16),
            (4, 17, 32),
            (8, 33, 64),
            (16, 65, 128),
            (0, 0, 0)
        ]
        
        try:
            for top_cut, min, max in attendance:
                self.cursor.execute(
                    "INSERT INTO tblTournamentAttendance (top_cut, min, max) VALUES (%s, %s, %s)",
                    (top_cut, min, max)
                )
            self.connection.commit()
            print("Initial data inserted into tblTournamentAttendance successfully")
        except mysql.connector.Error as err:
            print(f"Error inserting data into tblTournamentAttendance: {err}")
        
    def get_connection(self):
        return self.connection