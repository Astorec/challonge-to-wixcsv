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

    def check_participant_data(self,tournament_id, calls_instance):
        participants = calls_instance.get_participants(tournament_id)
        
        
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
            
            participant_db = self.modif_participants.create_participant(_participant.tournament_id, _participant.player_db_id, _participant.player_id, _participant.group_id)

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
        tournament_id = url
        calls_instance = calls.calls(username, api_key)
        previous_data = None
        last_check = False
        tournament_json = None
        current_tournament_json = None
        # Get Tournament Data from JSON File in config folder
        if not os.path.exists('config/tournament_data.json'):
            # Create the file
            with open('config/tournament_data.json', 'w') as f:
                f.write('[]')
                    
        with open('config/tournament_data.json') as f:
            tournament_json = json.load(f)
            
        for t in tournament_json:
            if t[0] == url:
                current_tournament_json = t
                break
                
        if self.modif_tournament.get_finalized_status(tournament_id) != 1:
        
            while True:
                try:
                    print("Checking...")
                    tournament_data = calls_instance.get_tournament(tournament_id)
                        
                    print("Tournament State: " + tournament_data['state'])
                                        
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
                                json.dump(tournament_json, f)
                        else:
                            current_tournament_json = tournament_json[url]
                            
                        
                    if previous_data is not None:    
                            
                        if tournament_data['state'] == 'complete':
                            print("Tournament completed. Doing final checks.")
                            last_check = True
                        if tournament_data['state'] == 'group_stages_underway':
                            self.is_two_stage = True                       
                            current_tournament_json['is_two_stage'] = True
                            with open('config/tournament_data.json', 'w') as f:
                                json.dump(tournament_json, f)
                            
                        if tournament_data != previous_data:
                            print("Data changed!")
                                
                            participant_count = tournament_data['participants_count']
                                
                            # compare participant count
                            if participant_count != tournament_db[3] and tournament_data['state'] == 'pending' or tournament_data['state'] == 'upcoming' or last_check:
                                tournament_db = self.update_participant_count(tournament_db, participant_count)
                                self.update_attendance_id(tournament_db)
                                self.check_participant_data
                                print("Participant count changed.")
                                print(f"New participant count: {tournament_db[3]}")
                                    
                        else:
                            print("No changes in Tournament Data detected.")
                            
                        if tournament_data['state'] == 'underway' or tournament_data['state'] == 'group_stages_underway' or last_check:
                            # Check match data
                            self.check_match_data(url, calls_instance)
                                
                            
                        # Get the players in the final stage check if the list is empty. If it's empty populate it
                        if last_check or current_tournament_json['is_two_stage'] == True and tournament_data['state'] == 'underway' and self.stage_two_participants.__len__() == 0:
                    
                            self.stage_two_participants = set_top_cut.get_finals_players(url, calls_instance, self.stage_two_participants, self.modif_tournament, self.modif_participants, self.modif_matches, self.modif_tournament_data)
                            
                                    
                    else:
                        is_new = True
                        print("Initial data fetched.")            
                        participant_count = tournament_data['participants_count']
                        # Check if tournament exists
                        if self.modif_tournament.get_tournament_by_url(url) is not None:
                            is_new = False
                            
                        tournament_db = self.modif_tournament.create_tournament(tournament_data['name'], url, participant_count, self.region.get_region_id_by_name(self.config['tournament_data']['region'])[0])
                            
                        # compare participant count
                        if participant_count != tournament_db[3] or is_new:
                            tournament_db = self.update_participant_count(tournament_db, participant_count)                    
                            self.update_attendance_id(tournament_db)
                            self.check_participant_data(tournament_id, calls_instance)
                            print("Participant count changed.")
                            print(f"New participant count: {tournament_db[3]}")
                            
                            
                        
                        if tournament_data['state'] == 'underway' or tournament_data['state'] == 'group_stages_underway' or is_new:
                            # Check match data
                            self.check_match_data(url, calls_instance)
                                
                    if last_check:
                        break   
                                
                    previous_data = tournament_data
                        
                    print(f"Next check in {interval} seconds. This Check will be at {datetime.now() + timedelta(seconds=interval)}")
                except Exception as e:
                    print(e)
                    
                time.sleep(interval)
    
        tournament_id = self.modif_tournament.get_tournament_by_url(url)[0]
            
        # Set the top cut
        set_top_cut.calculate_top_cut(tournament_id, tournament_db[6], self.stage_two_participants, self.get_top_cut, calls_instance, self.modif_matches, self.modif_players, self.modif_participants, self.modif_tournament, self.modif_tournament_data)
            
        results = self.generate_leaderboard_csv(tournament_id, tournament_db[5], "main_leaderboard.csv")
            
        wix_api.call(self.config, self.config['wix_api']['key'], self.config['wix_api']['site_id'], self.config['wix_api']['account_id'], results, tournament_db[1], self.region.get_region_by_id(tournament_db[5]), tournament_db[4])
            
    def generate_leaderboard_csv(self, tournament_id, region, filename):
        results = []
        
        results.append([self.leaderboard.get_main_board()])
    
        # Define the CSV headers
        headers = [
            "Rank", "Username", "Total Points" "Win Percentage", "Region"
        ]
        
        # If file exists, delete it
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        
        
        # Write the results to a CSV file
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            for data in results[0]:
                for row in data:
                    print(f"Row: {row}")
                    csvwriter.writerow(list(row))
                
            print(f"csvwriter: {csvwriter}")
        print(f"Main Leaderboard CSV file '{filename}' generated successfully.")
        
        
        results.append([self.leaderboard.get_tournament_leaderboard(tournament_id)])
        
        filename = f"{tournament_id}_leaderboard.csv"
        
        # If file exists, delete it
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
            for data in results[2]:
                for row in data:
                    print(f"Row: {row}")
                    csvwriter.writerow(list(row))
        
        
        print(f"Tournament Leaderboard CSV file '{filename}' generated successfully.")
        
        print(f"Results Length: {results.__len__()}")
        return results;


    def start(self):
        self.db = initDB.initDB('config/config.json').get_connection()

        self.modif_tournament = tournament.tournament(self.db)
        self.modif_participants = participants.participants(self.db)
        self.modif_players = players.player(self.db)
        self.modif_matches = matches.matches(self.db)
        self.modif_tournament_data = tournamentData.tournamentData(self.db)
        self.get_top_cut = top_cut.top_cut(self.db)
        self.leaderboard = leaderboard.leaderboard(self.db)
        self.region = region.region(self.db)
        
        username = self.config['challonge_api']['username']
        api_key = self.config['challonge_api']['key']
        url = misc.extract_tournament_id(self.config['challonge_api']['tournament_url'])
        self.check_periodically(username, api_key,  url, interval=5)


# Run the main class
if __name__ == "__main__":
    main().start()