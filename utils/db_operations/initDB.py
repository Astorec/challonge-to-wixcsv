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

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.config['db']['host'],
            user=self.config['db']['user'],
            password=self.config['db']['pass']
        )
        self.cursor = self.connection.cursor()
        # check if database exists
        self.cursor.execute("SHOW DATABASES")
        databases = self.cursor.fetchall()

        if (self.config['db']['db'],) in databases:
            self.cursor.execute(f"USE {self.config['db']['db']}")
            print(f"Using database {self.config['db']['db']}")
        else:
            self.cursor.execute(f"CREATE DATABASE {self.config['db']['db']}")
            self.cursor.execute(f"USE {self.config['db']['db']}")
            self.init_db()
            print(f"Database {self.config['db']['db']} created successfully")

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
                " is_store_championship tinyint(1) NULL DEFAULT 1,"
                " FOREIGN KEY (region) REFERENCES tblRegions(id),"
                " FOREIGN KEY (attendance_id) REFERENCES tblTournamentAttendance(id)"
                ");"
            ),
            'tblPlayers': (
                "CREATE TABLE IF NOT EXISTS tblPlayers ("
                " id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                " name VARCHAR(255) NOT NULL,"
                " username VARCHAR(255) NULL UNIQUE,"
                " region INT DEFAULT 13,"
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
            ),
            'tblParts':(
                "CREATE TABLE IF NOT EXISTS tblParts("
                " id INT AUTO_INCREMENT PRIMARY KEY,"
                " type VARCHAR(255) NOT NULL,"
                " name VARCHAR(255) NOT NULL);"
            )
        }

        for table_name, create_table_query in tables.items():
            try:
                self.cursor.execute(create_table_query)
                is_new = True
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
                ('Unassigned', 'UNASSIGNED')
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

            parts = [
                ('Assist Blade', 'Bumper'),
                ('Assist Blade', 'Round'),
                ('Assit Blade', 'Slash'),
                ('Lock Chip', 'Dran'),
                ('Lock Chip', 'Hells'),
                ('Lock Chip', 'Perseus'),
                ('Lock Chip', 'Wizard'),
                ('Assist Blade', 'Bumper'),
                ('Assist Blade', 'Round'),
                ('Assit Blade', 'Slash'),
                ('Lock Chip', 'Dran'),
                ('Lock Chip', 'Hells'),
                ('Lock Chip', 'Perseus'),
                ('Lock Chip', 'Wizard'),
                ('Bit', 'Accel'),
                ('Bit', 'Ball'),
                ('Bit', 'Bound Spike'),
                ('Bit', 'Cyclone'),
                ('Bit', 'Disk Ball'),
                ('Bit', 'Dot'),
                ('Bit', 'Elevate'),
                ('Bit', 'Free Ball'),
                ('Bit', 'Gear Ball'),
                ('Bit','Gear Flat'),
                ('Bit', 'Gear Needle'),
                ('Bit', 'Gear Point'),
                ('Bit', 'Glide'),
                ('Bit', 'Hexa'),
                ('Bit', 'High Needle'),
                ('Bit', 'High taper'),
                ('Bit', 'Level'),
                ('Bit', 'Low Flat'),
                ('Bit', 'Low Orb'),
                ('Bit', 'Low Rush'),
                ('Bit', 'Metal Needle'),
                ('Bit', 'Needle'),
                ('Bit', 'Orb'),
                ('Bit', 'Point'),
                ('Bit', 'Quake'),
                ('Bit', 'Rubber Acce'),
                ('Bit', 'Rush'),
                ('Bit', 'Spike'),
                ('Bit', 'Taper'),
                ('Bit', 'Trans Point'),
                ('Bit', 'Under Needle'),
                ('Bit', 'Unite'),
                ('Bit', 'Vortex'),
                ('Bit', 'Wedge'),
                ('Blade', 'AeroPegasus'),
                ('Blade', 'Bite Croc'),
                ('Blade', 'Black Shell'),
                ('Blade', 'Captain America'),
                ('Blade', 'CobaltDragoon'),
                ('Blade', 'CobaltDrake'),
                ('Blade', 'CrimsonGaruda'),
                ('Blade', 'Darth Vader'),
                ('Blade', 'DracielShield'),
                ('Blade', 'DragoonStorm'),
                ('Blade', 'Dran Buster'),
                ('Blade', 'DranDagger'),
                ('Blade', 'DranSword'),
                ('Blade', 'DranzerSpiral'),
                ('Blade', 'DrigerSlash'),
                ('Blade', 'Ghost Circle'),
                ('Blade', 'GolemRock'),
                ('Blade', 'Hells Hammer'),
                ('Blade', 'HellsChain'),
                ('Blade', 'HellsScythe'),
                ('Blade', 'Hover Wyvern'),
                ('Blade', 'Impact Drake'),
                ('Blade', 'Iron Man'),
                ('Blade', 'Knife Shinobi'),
                ('Blade', 'KnightLance'),
                ('Blade', 'KnightMail'),
                ('Blade', 'KnightShield'),
                ('Blade', 'Leon Claw'),
                ('Blade', 'LeonCrest'),
                ('Blade', 'Lightning L-Drago (Rapid-Hit Type)'),
                ('Blade', 'Lightning L-Drago (Upper Type)'),
                ('Blade', 'Luke Skywalker'),
                ('Blade', 'Megatron'),
                ('Blade', 'Moff Gideon'),
                ('Blade', 'Optimus Primal'),
                ('Blade', 'Optimus Prime'),
                ('Blade', 'Phoenix Rudder'),
                ('Blade', 'Phoenix Wing'),
                ('Blade', 'PhoenixFeather'),
                ('Blade', 'Red Hulk'),
                ('Blade', 'Rhino Horn'),
                ('Blade', 'Roar Tyranno'),
                ('Blade', 'SamuraiSaber'),
                ('Blade', 'Savage Bear'),
                ('Blade', 'SharkEdge'),
                ('Blade', 'Shelter Drake'),
                ('Blade', 'Shinobi Shadow'),
                ('Blade', 'SilverWolf'),
                ('Blade', 'Sphinx Cowl'),
                ('Blade', 'Spider-Man'),
                ('Blade', 'Starscream'),
                ('Blade', 'Steel Samurai'),
                ('Blade', 'Storm Pegasis'),
                ('Blade', 'Talon Ptera'),
                ('Blade', 'Thanos'),
                ('Blade', 'The Mandalorian'),
                ('Blade', 'Tusk Mammoth'),
                ('Blade', 'Tyranno Beat'),
                ('Blade', 'Unicorn Sting'),
                ('Blade', 'Venom'),
                ('Blade', 'Victory Valkyrie'),
                ('Blade', 'Viper Tail'),
                ('Blade', 'WeissTiger'),
                ('Blade', 'Whale Wave'),
                ('Blade', 'Wizard Rod'),
                ('Blade', 'WizardArrow'),
                ('Blade', 'Wyvern Gale'),
                ('Blade', 'Yell Kong'),
                ('Main Blade', 'Arc'),
                ('Main Blade', 'Brave'),
                ('Main Blade', 'Dark'),
                ('Main Blade', 'Reaper'),
                ('Ratchet', '0-80'),
                ('Ratchet', '1-60'),
                ('Ratchet', '1-80'),
                ('Ratchet', '2-60'),
                ('Ratchet', '2-70'),
                ('Ratchet', '2-80'),
                ('Ratchet', '3-60'),
                ('Ratchet', '3-70'),
                ('Ratchet', '3-80'),
                ('Ratchet', '3-85'),
                ('Ratchet', '4-55'),
                ('Ratchet', '4-60'),
                ('Ratchet', '4-70'),
                ('Ratchet', '4-80'),
                ('Ratchet', '5-60'),
                ('Ratchet', '5-70'),
                ('Ratchet', '5-80'),
                ('Ratchet', '6-60'),
                ('Ratchet', '6-80'),
                ('Ratchet', '7-60'),
                ('Ratchet', '7-70'),
                ('Ratchet', '7-80'),
                ('Ratchet', '9-60'),
                ('Ratchet', '9-70'),
                ('Ratchet', '9-80')
            ]

            try:
                for type, name in parts:
                    self.cursor.execute(
                        "INSERT INTO tblParts (type, name) VALUES (%s, %s)",
                        (type, name)
                    )
                self.connection.commit()
                print("Initial data inserted into tblParts successfully")
            except mysql.connector.Error as err:
                print(f"Error inserting data into tblParts: {err}")

    def get_connection(self):
        return self.connection