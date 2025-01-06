import os
import smtplib
import csv
import requests
from imap_tools import MailBox, A
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
import api.challonge.calls as calls
import time
import json
import utils.db_operations.initDB as initDB
import utils.db_operations.tournament as tournament
import utils.db_operations.tournamentData as tournamentData
import utils.db_operations.participants as participants
import utils.db_operations.player as players
import utils.db_operations.matches as matches
from urllib.parse import urlparse
from datetime import datetime, timedelta
from decimal import Decimal

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class player:
    def __init__(self, name, username = None):
        self.name = name
        self.username = username
        pass
        
class participant:
     def __init__(self, player_db_id, tournament_id, player_id, group_id):
        self.player_db_id = player_db_id
        self.tournament_id = tournament_id
        self.player_id = player_id
        self.group_id = group_id
        pass
        
        
class main:
    
    
    def __init__(self):
        app = Flask(__name__)
        self.config = None
        self.confirmation_response = None


        # Check if config/config.json exists
        if os.path.exists('config/config.json'):
            with open('config/config.json') as f:
                self.config = json.load(f)
        else:
            print("Check that config file exists within conifg folder.")
            raise FileNotFoundError("Config file not found.")
        

    def send_email(self, subject, body, to_email):
        from_email = self.config['email']['email_send_from']
        password = self.config['email']['password']

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self.config['email']['smtp_address'], self.config['email']['smtp_port'])
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
    def check_for_confirmation_response(self, tournament_id):
        with MailBox(self.config['email']['iamp_address']).login(self.config['email']['email_send_from'], self.config['email']['password'], self.config['email']['folder']) as mailbox:
            for msg in mailbox.fetch(A(subject=f'Top 8 Confirmation {tournament_id}')): 
                try:
                    # Extract the email body
                    email_body = msg.text or msg.html or msg.body
                    if email_body:
                        # Parse the email body as JSON
                        self.confirmation_response = json.loads(email_body)
                    else:
                        print("No valid data found in the email body.")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from email: {e}")
                except Exception as e:
                    print(f"Error processing email: {e}")
        return None

    def calculate_top_8(self,tournament_id):
        top_8 = {}
        
        query = """
        SELECT 
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
        LIMIT 8;
        """
        
        cursor = self.db.cursor()
        cursor.execute(query, (tournament_id,))
        results = cursor.fetchall()
        
        rank_labels = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
        for i, row in enumerate(results):
            top_8[rank_labels[i]] = {
                "name": row[0],
                "username": row[1]
            }
        
        cursor.close()
        return top_8


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

    def check_participant_data(self,tournament_id, calls_instance):
        participants = calls_instance.get_participants(tournament_id)
        
        
        for p in participants:
            print(f"Adding participant {p['name']}")
            
            # Check if player exists
            player_db = self.modif_players.get_player_by_username(p['username'])
            if player_db is None:
                _player = player(p['name'], p['username'])
                player_db = self.modif_players.create_player(_player.name, _player.username)
                if player_db is None:
                    print(f"Failed to create player: {_player.name}, {_player.username}")
                    continue
                
    
            t_id = self.modif_tournament.get_tournament_by_url(tournament_id)[0]
            
            print(f"Adding participant {p['name']} to tournament {t_id}. Player ID: {p['id']} Group ID: {p['group_player_ids'][0]}")
            _participant = participant(player_db[0], t_id, p['id'], p['group_player_ids'][0])   
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
            match_db = self.modif_matches.get_match_by_id(m['id'])
            if match_db is None:
                if m['player1_id'] is None and m['player2_id'] is None:
                    print(f"Error: Match with ID {m['id']} has no player IDs. Skipping...")
                    continue
                match_db = self.modif_matches.add_match(m['player1_id'], m['player2_id'], tournament_db[0])
                if match_db is None:
                    print(f"Error: Failed to add match with ID {m['id']}. Player 1 ID was: {m['player1_id']}, Player 2 ID was: {m['player2_id']}. Skipping...")
                    continue
            
            
            
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
                self.modif_tournament_data.undo_win(tournament_db[0], winner_player_id)
                self.modif_tournament_data.undo_loss(tournament_db[0], loser_player_id)
                match_db = self.modif_matches.undo_match_winner(match_db[0])
                if match_db is None:
                    print(f"Error: Failed to undo match winner for match ID {m['id']}.")
                continue

    def wix_api(self, api_key, site_id, account_id, data):
        headers= {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "wix-account-id": account_id,
            "wix-site-id": site_id
        }
        
        post_data = {
            "dataCollectionId": self.config['wix_collection']['collection_id']
        }
        
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
        
        if current_data.status_code == 200:
            print("Got the view data")
            
        data_item_ids = []
        
        for item in current_data.json()['dataItems']:
            data_item_ids.append(item['id'])
        
        if len(data_item_ids) > 0:
            delete_data = {
                "dataCollectionId": self.config['wix_collection']['collection_id'],
                "dataItemIds": data_item_ids
            }
            requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/remove", headers=headers, data=json.dumps(delete_data))
        
        data_items = []
        
        for row in data:
            print(f"Points: {row[2]}")
            data_items.append({
                "data": {
                    
                    "rank": row[0],
                    "username": row[1],
                    "total_points": row[2]
                }
            })
            
        post_data = {
            "dataCollectionId": "Import216",
            "dataItems": data_items
        }
        
        print(f"Data Items: {data_items}")
        
        requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/insert", headers=headers, data=json.dumps(post_data, cls=DecimalEncoder))
        
    def check_periodically(self, username, api_key, url, interval=30):
        tournament_id = self.extract_tournament_id(url)
        calls_instance = calls.calls(username, api_key)
        previous_data = None
        last_check = False
        
        while True:
            try:
                print("Checking...")
                tournament_data = calls_instance.get_tournament(tournament_id)
                
                if previous_data is not None:
                    if tournament_data['state'] == 'complete':
                        print("Tournament completed. Doing final checks.")
                        last_check = True
                    
                    if tournament_data != previous_data:
                        print("Data changed!")
                        
                        # Check specific data
                        current_state = tournament_data['state']
                        participant_count = tournament_data['participants_count']
                        
                        # compare participant count
                        if participant_count != tournament_db[3] and tournament_data['state'] == 'pending' or tournament_data['state'] == 'upcoming':
                            tournament_db = self.update_participant_count(tournament_db, participant_count)
                            self.check_participant_data
                            print("Participant count changed.")
                            print(f"New participant count: {tournament_db[3]}")
                        
                        # Compare state
                        if current_state != tournament_db[5]:
                            tournament_db = self.update_state(tournament_db, current_state)
                            print("State changed.")
                            print(f"New state: {tournament_db[5]}")
                            
                    else:
                        print("No changes in Tournament Data detected.")
                    
                    if tournament_data['state'] == 'underway':
                        # Check match data
                        self.check_match_data(url, calls_instance)
                else:
                    is_new = True
                    print("Initial data fetched.")                
                    current_state = tournament_data['state']
                    participant_count = tournament_data['participants_count']
                    # Check if tournament exists
                    if self.modif_tournament.get_tournament_by_url(url) is not None:
                        is_new = False
                    
                    tournament_db = self.modif_tournament.create_tournament(tournament_data['name'], url, participant_count)
                    
                    # compare participant count
                    if participant_count != tournament_db[3] or is_new:
                        tournament_db = self.update_participant_count(tournament_db, participant_count)                    
                        self.check_participant_data(tournament_id, calls_instance)
                        print("Participant count changed.")
                        print(f"New participant count: {tournament_db[3]}")
                    
                    # Compare state
                    if current_state != tournament_db[5]:
                        tournament_db = self.update_state(tournament_db, current_state)
                        print("State changed.")
                        print(f"New state: {tournament_db[5]}")
                    
                
                    if tournament_data['state'] == 'underway' or is_new:
                        # Check match data
                        self.check_match_data(url, calls_instance)
                
                if last_check:
                    break   
                        
                previous_data = tournament_data
                
                print(f"Next check in {interval} seconds. This Check will be at {datetime.now() + timedelta(seconds=interval)}")
            except Exception as e:
                print(e)
            
            time.sleep(interval)
        
        if tournament_data['state'] == 'complete':
            wix_api_key = self.config['wix_api']['key']
            wix_site_id = self.config['wix_api']['site_id']
            wix_account_id = self.config['wix_api']['account_id']
            
            
            tournament_id = self.modif_tournament.get_tournament_by_url(url)[0]
            top_8 = json.dumps(self.calculate_top_8(tournament_id), indent=4)
            body = f"The tournament is completed. The potential top 8 players are: \n{top_8}\n\n Respond to this email with the correct top 8 and change the subject heading to 'Top 8 Confirmation {tournament_id}'."
            self.send_email("Tournament Completed", body,  self.config['email']['email_send_to'])
            print("Email sent with potential top 8 players.")
            
            # Wait for confirmation response
            print("Waiting for confirmation response...")
            while True:
                # Check for confirmation response
                response = self.check_for_confirmation_response(tournament_id)
                if response:
                    # Update the database with the confirmed top 8 players
                    self.update_top_8_in_db(tournament_id, response)
                    print("Top 8 confirmed and updated in the database.")
                    results = self.generate_leaderboard_csv("leaderboard.csv")
                    self.wix_api(wix_api_key, wix_site_id, wix_account_id, results)
                    break
                
                print("No confirmation response yet. Checking again in 5 seconds.")    
                time.sleep(5)  # Check every 30 seconds
        
    def extract_tournament_id(self, url):
        parsed_url = urlparse(url)
        netloc_parts = parsed_url.netloc.split('.')
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(netloc_parts) == 3 and netloc_parts[0] != 'www':
            subdomain = netloc_parts[0]
            tournament_id = path_parts[0]
            return f"{subdomain}-{tournament_id}"
        elif len(path_parts) == 1:
            return path_parts[0]
        else:
            raise ValueError("Invalid URL format")

    def update_top_8_in_db(self, tournament_id, top_8):
        for i, (placement, player) in enumerate(top_8.items()):
            player_db = self.modif_players.get_player_by_username(player['username'])
            if player_db is None:
                player_db = self.modif_players.create_player(player['name'], player['username'])
            self.modif_tournament_data.add_placement(tournament_id, player_db[0], i + 1)
        pass

    def generate_leaderboard_csv(self, filename):
        results = self.modif_tournament_data.sort_data_by_score_add_rank()
    
        # Define the CSV headers
        headers = [
            "Rank", "Username", "Total Points"
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
            csvwriter.writerows(results)
        print(f"Leaderboard CSV file '{filename}' generated successfully.")
        
        return results;


    def start(self):
        self.db = initDB.initDB('config/config.json').get_connection()

        self.modif_tournament = tournament.tournament(self.db)
        self.modif_participants = participants.participants(self.db)
        self.modif_players = players.player(self.db)
        self.modif_matches = matches.matches(self.db)
        self.modif_tournament_data = tournamentData.tournamentData(self.db)
        username = self.config['challonge_api']['username']
        api_key = self.config['challonge_api']['key']
        self.check_periodically(username, api_key, self.extract_tournament_id(self.config['challonge_api']['tournament_url']), interval=5)


# Run the main class
if __name__ == "__main__":
    main().start()