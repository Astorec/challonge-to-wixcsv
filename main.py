import os
import csv
import api.challonge.calls as calls
import time
import json
import utils.db_operations.initDB as initDB
import utils.db_operations.tournament as tournament
import utils.db_operations.tournamentData as tournamentData
import utils.db_operations.participants as participants
import utils.db_operations.player as players
import utils.db_operations.matches as matches
import utils.db_operations.top_cut as top_cut
import utils.db_operations.leaderboard as leaderboard
import utils.db_operations.region as region
import utils.misc as misc
import utils.wix_calls.wix_api as wix_api
import utils.leaderboard.top_cut as set_top_cut

from classes.player import player
from classes.participant import participant
from urllib.parse import urlparse
from datetime import datetime, timedelta
from flask import Flask

class main:
    def __init__(self):
        app = Flask(__name__)
        self.config = None
        self.confirmation_response = None
        self.is_two_stage = False
        self.stage_two_participants = []


        # Check if config/config.json exists
        if os.path.exists('config/config.json'):
            with open('config/config.json') as f:
                self.config = json.load(f)
        else:
            print("Check that config file exists within conifg folder.")
            raise FileNotFoundError("Config file not found.")


    def update_participant_count(self, db, participant_count):
        print("Participant count changed.")
        print(f"Old participant count: {db[3]}")
        print(f"New participant count: {participant_count}")
        # Update attendance ID if participant count meets the requirements
        if participant_count == 4:
            attendance_id = 1
        elif participant_count <= 16:
            attendance_id = 2
        elif participant_count <= 63:
            attendance_id = 3
        elif participant_count <= 119:
            attendance_id = 4
        elif participant_count <= 999:
            attendance_id = 5
        else:
            attendance_id = 6
        self.modif_tournament.set_attendance_id(db[0], attendance_id)
        return self.modif_tournament.update_participant_count(db[0], participant_count)
    

    def update_state(self, db, state):
        print("State changed.")
        print(f"Old state: {db[5]}")
        print(f"New state: {state}")
        return self.modif_tournament.update_state(db[0], state)

    def update_attendance_id(self, db):
       if db[6] == 6:
            if db[3] <= 8:
                self.modif_tournament.set_attendance_id(db[0], 1)
            elif db[3] <= 16:
                self.modif_tournament.set_attendance_id(db[0], 2)
            elif db[3] <= 32:
                self.modif_tournament.set_attendance_id(db[0], 3)
            elif db[3] <= 64:
                self.modif_tournament.set_attendance_id(db[0], 4)
            elif db[3] <= 128:
                self.modif_tournament.set_attendance_id(db[0], 5)

    def check_participant_data(self,tournament_id, participants):
        
        
        for p in participants:
            print(f"Adding participant {p['name']}")
            
            
            player_db = None
            
            
            if p['username'] is not None:
                player_db = self.modif_players.get_player_by_username(p['username'])
            elif p['name'] is not None:
                player_db = self.modif_players.get_player_by_name(p['name'])
            
            
            if player_db is None:
                _player = player(p['name'], p['username'])
                player_db = self.modif_players.create_player(_player.name, _player.username)
                if player_db is None:
                    print(f"Failed to create player: {_player.name}, {_player.username}")
                    continue                
    
            t_id = self.modif_tournament.get_tournament_by_url(tournament_id)[0]
            
            print(f"Adding participant {p['name']} to tournament {t_id}")
            
            if len(p['group_player_ids']) > 0:                            
                _participant = participant(player_db[0], t_id, p['id'], p['group_player_ids'][0])   
            else:
                _participant = participant(player_db[0], t_id, p['id'])    
            
            self.modif_participants.create_participant(_participant.tournament_id, _participant.player_db_id, _participant.player_id, _participant.group_id)

            if self.modif_tournament_data.get_data(t_id, player_db[0]) is None:
                self.modif_tournament_data.add_data(t_id, player_db[0])
    
        # After adding players, check if any players have been removed
        db_participants = self.modif_participants.get_participants_by_tournament_id(tournament_id)
        for p in db_participants:
            found = False
            for p2 in participants:
                if p[3] == p2['id']:
                    found = True
                    break
            if not found:
                self.modif_participants.delete_participant(p[0])
                print(f"Participant {p[0]} has been removed.")

    def check_match_data(self, tournament_id, calls_instance):
        matches = calls_instance.get_matches(tournament_id)
        
        # Get tournament ID from DB
        tournament_db = self.modif_tournament.get_tournament_by_url(tournament_id)
        if tournament_db is None:
            print(f"Error: Tournament with ID {tournament_id} not found in DB.")
            return
        
        for m in matches:
            print(f"Processing match with ID {m['id']}")
            match_db = self.modif_matches.get_match_by_id(m['id'])
            print(match_db)
            if match_db is None:
                print(f"Match with ID {m['id']} not found in database.")
                if m['player1_id'] is None and m['player2_id'] is None:
                    print(f"Error: Match with ID {m['id']} has no player IDs. Skipping...")
                    continue
                print(f"Adding match with ID {m['id']}, Player 1 ID: {m['player1_id']}, Player 2 ID: {m['player2_id']}")
                match_db = self.modif_matches.add_match(m['id'], m['player1_id'], m['player2_id'], tournament_db[0])
                
         
                
                if match_db is None:
                    print(f"Error: Failed to add match with ID {m['id']}. Player 1 ID was: {m['player1_id']}, Player 2 ID was: {m['player2_id']}. Skipping...")
                    continue
            
            if self.modif_participants.get_participant_by_id_tournament_id(m['player1_id'], tournament_db[0]) is not None or self.modif_participants.get_participant_by_id_tournament_id(m['player2_id'], tournament_db[0]) is not None:
                self.modif_matches.set_match_to_final(match_db[7])

            
            if match_db[3] is None and match_db[4] is None:
            
                # Check if there is a winner ID
                if m['winner_id'] is not None and match_db[3] is None:
                    
                    
                    winner_player = self.modif_participants.get_participant_by_player_id_tournament_id(m['winner_id'], tournament_db[0])
                    loser_player = self.modif_participants.get_participant_by_player_id_tournament_id(m['loser_id'], tournament_db[0])
                    
                    if winner_player and loser_player:
                        winner_player_id = winner_player[0][0]  # Extract the player ID from the tuple
                        loser_player_id = loser_player[0][0]  # Extract the player ID from the tuple
                        
                        winner_player_id = self.modif_participants.get_participant_by_player_id_tournament_id(m['winner_id'], tournament_db[0])[0][1]
                        loser_player_id = self.modif_participants.get_participant_by_player_id_tournament_id(m['loser_id'], tournament_db[0])[0][1]
                        match_db = self.modif_matches.update_match_winner(match_db[0], m['winner_id'], m['loser_id'])
                        if match_db is None:
                            print(f"Error: Failed to update match winner for match ID {m['id']}.")
                            continue
                        
                        
                        
                        # Update Tournament Data
                        self.modif_tournament_data.add_win(tournament_db[0], winner_player_id)
                        self.modif_tournament_data.add_loss(tournament_db[0], loser_player_id)
                        continue
                
            # Check if there is not a winner ID but was previously set
            if m['winner_id'] is None and match_db[3] is not None:
                winner_player_id = match_db[3]
                loser_player_id = match_db[4]
                self.modif_tournament_data.remove_win(tournament_db[0], winner_player_id)
                self.modif_tournament_data.remove_loss(tournament_db[0], loser_player_id)
                match_db = self.modif_matches.undo_match_winner(match_db[0])
                if match_db is None:
                    print(f"Error: Failed to undo match winner for match ID {m['id']}.")
                continue

    def check_periodically(self, username, api_key, url, interval=30):
        # The tournament id is extracted from the URL which we do before passing it in to the function
        tournament_id = url
        
        # Calls instance is used to make calls to the Challonge API
        calls_instance = calls.calls(username, api_key)

        # Initialize variables
        previous_data = None
        previous_data_participants = None
        last_check = False
        tournament_json = None
        current_tournament_json = None


        # Get Tournament Data from JSON File in config folder. This is mostly used
        # for tracking the two stage tournament, but I'm debating removing it as
        # I think I can store this data in the database easily enough and shoudln't 
        # need to be a separate file.

        #region Tournament Data JSON
        if not os.path.exists('config/tournament_data.json'):
            # Create the file
            with open('config/tournament_data.json', 'w') as f:
                f.write('{}')
                    
        with open('config/tournament_data.json') as f:
            tournament_json = json.load(f)
            
        for t in tournament_json:
            if t[0] == url:
                current_tournament_json = t
                break
        #endregion
        
        # Check if the tournament is finalized. The finalized status is set to 1 after all
        # stages of the tournament have been completed, so that we don't make unnecessary calls
        if self.modif_tournament.get_finalized_status(tournament_id) != 1:
            
            # Check the tournament state every interval seconds. This is set within the config json
            while True:
                try:
                    print("Checking...")
                    
                    # Ge the tournament data from the Challonge API
                    tournament_data = calls_instance.get_tournament(tournament_id)
                        
                    print("Tournament State: " + tournament_data['state'])

                    # We check the states of the tournament to see what we need to do. If the tournament is complete
                    # or is awaiting review we can set the last_check to true to ensure that all the data is up to date
                    # before generating the leaderboards
                    if tournament_data['state'] == 'complete' or tournament_data['state'] == 'awaiting_review':      
                        last_check = True
                        print("Last check.")  

                    # If the current_json is None, we try and get the data from the json file. Again like above
                    # This could be updated to be done Via the DB is still here from the inital code         
                    if current_tournament_json is None:
                    # try and get data from json
                        with open('config/tournament_data.json') as f:
                            tournament_json = json.load(f)
                        # find tournament url in json
                        if url not in tournament_json:
                            current_tournament_json = {
                                "name": tournament_data['name'],
                                "participant_count": tournament_data['participants_count'],
                                "is_two_stage": False
                            }
                            tournament_json[url] = current_tournament_json
                            with open('config/tournament_data.json', 'w') as f:
                                json.dump(tournament_json, f, indent=4)
                        else:
                            current_tournament_json = tournament_json[url]
                            
                    # If the previous data is not None, we can compare the data to see if there are any changes   
                    if previous_data is not None:    
                        
                        # Get the Participants from the API
                        participants = calls_instance.get_participants(tournament_id)

                        # IF there has been any changes to the participants and we are in a pending state, upcoming state or it's the last check
                        # we can update the data in the database
                        if participants != previous_data_participants and tournament_data['state'] == 'pending' or tournament_data['state'] == 'upcoming' or last_check:
                            
                            if participants.__len__() == 0:
                                print("No participants found.")

                            if participants.__len__() != 0:
                                if participants.__len__() != tournament_data['participants_count']:

                                    print("Participants changed.") 

                                    # compare participant counts
                                    participant_count = tournament_data['participants_count']

                                    # Update the Participant count for the tournament
                                    tournament_db = self.update_participant_count(tournament_db, participant_count)

                                    # Check if we need to update the Attendance ID. This is relevant as tblAttendance
                                    # determins the Top Cut for the tournament
                                    self.update_attendance_id(tournament_db)

                                    # Check the participant data
                                    self.check_participant_data(tournament_id, participants)
                                    print("Participant count changed.")
                                    print(f"New participant count: {tournament_db[3]}")
                                    
                                    # Set previous participants to current participants
                                    previous_data_participants = participants

                                # If the state is set to complete, we can initalise a final check on the next loop
                                if tournament_data['state'] == 'complete':
                                    print("Tournament completed. Doing final checks.")  
                                    last_check = True

                                if tournament_data['state'] == 'group_stages_underway':
                                    self.is_two_stage = True                       
                                    current_tournament_json['is_two_stage'] = True

                                    #  Double check that we have the correct data in the JSON file
                                    self.check_participant_data(tournament_id, participants)
                                    with open('config/tournament_data.json', 'w') as f:
                                        json.dump(tournament_json, f)
                              
                        else:
                            print("No changes in Tournament Data detected.")
                        

                        # If the state is set to underway, we can start to pull the match data and check for
                        # updates. The tournament should alwyas be setup as two stage so group_stages_underway
                        # should be the state that returns when the tournament is in the group stages
                        if tournament_data['state'] == 'underway' or tournament_data['state'] == 'group_stages_underway' or last_check:
                            # Check match data
                            self.check_match_data(url, calls_instance)
                                
                            
                        # Get the players in the final stage check if the list is empty. If it's empty populate it
                        if last_check or current_tournament_json['is_two_stage'] == True and tournament_data['state'] == 'underway' and self.stage_two_participants.__len__() == 0:
                    
                            self.stage_two_participants = set_top_cut.get_finals_players(url, calls_instance, self.stage_two_participants, self.modif_tournament, self.modif_participants, self.modif_matches, self.modif_tournament_data)

                    # This is the same as above but there are some differences to ensure that we are getting the correct data
                    # on the first run with this tournament.
                    else:
                        is_new = True
                        print("Initial data fetched.")            
                        participant_count = tournament_data['participants_count']
                        participants = calls_instance.get_participants(tournament_id)
                        get_tournament = self.modif_tournament.get_tournament_by_url(url)
                        # Check if tournament exists
                        if get_tournament is not None:

                            is_new = False
                            if self.modif_tournament.get_championship_type(get_tournament[0])[0]is not self.config['tournament_data']['is_store_championship']:
                                # False is 0 and True is 1
                                get_tournament = self.modif_tournament.set_championship_type(get_tournament[0], self.config['tournament_data']['is_store_championship'])
                            
                        tournament_db = self.modif_tournament.create_tournament(tournament_data['name'], url, participant_count, self.region.get_region_id_by_name(self.config['tournament_data']['region'])[0])
                            
                        # compare participant count
                        if participant_count != tournament_db[3] or is_new:
                            tournament_db = self.update_participant_count(tournament_db, participant_count)                    
                            self.update_attendance_id(tournament_db)
                            self.check_participant_data(tournament_id, participants)
                            print("Participant count changed.")
                            print(f"New participant count: {tournament_db[3]}")
                            
                            
                        
                        if tournament_data['state'] == 'underway' or tournament_data['state'] == 'group_stages_underway' or is_new:
                            # Check match data
                            self.check_match_data(url, calls_instance)

                        if last_check:
                            self.check_match_data(url, calls_instance)
                                
                    if last_check:
                        break   
                                
                    previous_data = tournament_data
                except Exception as e:
                    print(e)    
                    # Print how much time is left until the next check and update the secondsl left
                while interval > 0:
                    # Decrese the interval every second
                    interval -= 1
                    # delete the previous line
                    print("\033[A                             \033[A")
                    print(f"Next check in {interval} seconds. This Check will be at {datetime.now() + timedelta(seconds=interval)}")
                    time.sleep(1)
                interval = self.config['challonge_api']['interval']
                
                    
        # If the tournament is finalized, we can generate the leaderboards.
                
        # Get the tournament data from the database. This is so that we have the most up to date version
        tournament = self.modif_tournament.get_tournament_by_url(url)
        
        # Calculate the top_cut from the tournament data
        if tournament[7] == 0:
            # Set the top cut
            set_top_cut.calculate_top_cut(tournament[0], tournament[6], self.stage_two_participants, self.get_top_cut, calls_instance, self.modif_matches, self.modif_players, self.modif_participants, self.modif_tournament, self.modif_tournament_data)
        

        # Generate the Boards and output them to CSV Files. We generate the Date and time in the event of modifications that occur
        dateTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
        results = self.generate_leaderboard_csv(tournament[0], tournament[5], "main_leaderboard.csv", dateTime)
        print("CSV files generated. Checking if Wix API is configured.")

        # We only make the WIX API calls if the WIX API has been configured
        if self.config['wix_api']['key'] is not None and self.config['wix_api']['site_id'] is not None and self.config['wix_api']['account_id'] is not None:
            print("Wix API configured. Making Wix API call.")
            wix_api.call(dateTime, self.config, self.config['wix_api']['key'], self.config['wix_api']['site_id'], self.config['wix_api']['account_id'], results, tournament[1], self.region.get_region_by_id(tournament[5]), tournament[4])
        else:
            print("Wix API not configured. Skipping Wix API call.")


    # Generate the CSV files for the leaderboards. Returns the results for when the WIX api is configured
    def generate_leaderboard_csv(self, tournament_id, region, filename, dateTime):
        results = []
        
        results.append([self.leaderboard.get_main_board()])
    
        # Define the CSV headers
        headers = [
            "Rank", "Username", "Total Points", "Win Percentage", "Region"
        ]       

        # We only generate the Main and Region baords if it is a store championship       
        if self.config['tournament_data']['is_store_championship'] == 1:
            #region Main Board
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(headers)
                for data in results[0]:
                    for row in data:
                        print(f"Row: {row}")
                        csvwriter.writerow(list(row))
                    
                print(f"csvwriter: {csvwriter}")
            print(f"Main Leaderboard CSV file '{filename}' generated successfully.")
            #endregion
            
            #region Region Leaderboard
            results.append([self.leaderboard.get_region_leaderboard(region)])
            
            filename = f"{self.region.get_region_by_id(region)[1]}_leaderboard.csv"
            
            #if file exists, delete it
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
            
            # Write the results to a CSV file
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(headers)            
                for data in results[1]:
                    for row in data:
                        print(f"Row: {row}")
                        csvwriter.writerow(list(row))
            #endregion

        # Always generate the Tournament board
        #region Tournament Leaderboard
        torunament = self.modif_tournament.get_tournament_by_id(tournament_id)
        results.append([self.leaderboard.get_tournament_leaderboard(tournament_id)])
        
        tournament_name = torunament[1]
        # Remove any slashes from the tournament name
        tournament_name = tournament_name.replace("/", "_")
        tournament_name = tournament_name.replace(" ", "_")       


        filename = f"{tournament_name}_{dateTime}_leaderboard.csv"
        # If file exists, delete it
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

        
        # Write the results to a CSV file
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            # if is not store championship, loop through results[0]
            if self.config['tournament_data']['is_store_championship'] == 0:
                for data in results[0]:
                    for row in data:
                        print(f"Row: {row}")
                        csvwriter.writerow(list(row))
            else:
                for data in results[2]:
                    for row in data:
                        print(f"Row: {row}")
                        csvwriter.writerow(list(row))
        #endregion
        
        print(f"Tournament Leaderboard CSV file '{filename}' generated successfully.")
        
        print(f"Results Length: {results.__len__()}")
        return results;


    def start(self):
        # Generate the Database from the config file
        self.db = initDB.initDB('config/config.json').get_connection()

        # Create instances of the classes for DB operations
        #region DB Class Initialization
        self.modif_tournament = tournament.tournament(self.db)
        self.modif_participants = participants.participants(self.db)
        self.modif_players = players.player(self.db)
        self.modif_matches = matches.matches(self.db)
        self.modif_tournament_data = tournamentData.tournamentData(self.db)
        self.get_top_cut = top_cut.top_cut(self.db)
        self.leaderboard = leaderboard.leaderboard(self.db)
        self.region = region.region(self.db)
        #endregion
        
        #region Challonge Settings
        username = self.config['challonge_api']['username']
        api_key = self.config['challonge_api']['key']
        url = misc.extract_tournament_id(self.config['challonge_api']['tournament_url'])
        #endregion
    
        self.check_periodically(username, api_key,  url, interval=self.config['challonge_api']['interval'])


# Run the main class
if __name__ == "__main__":
    main().start()