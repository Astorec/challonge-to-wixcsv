import asyncio
import time
import json
import os
from datetime import datetime, timedelta
import logging

import api.challonge.calls as calls
import utils.misc as misc
import utils.leaderboard.top_cut as set_top_cut

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tournament_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tournament_monitor')

class TournamentMonitor:
    def __init__(self, config, db_connections, tournament_id):
        self.config = config
        self.tournament_id = tournament_id
        self.is_two_stage = False
        self.stage_two_participants = []
        self.stop_monitor = False
        self.last_state = None
        self.calls_instance = None
        
        # DB connections
        self.db = db_connections["db"]
        self.modif_tournament = db_connections["tournament"]
        self.modif_participants = db_connections["participants"]
        self.modif_players = db_connections["players"]
        self.modif_matches = db_connections["matches"]
        self.modif_tournament_data = db_connections["tournament_data"]
        self.get_top_cut = db_connections["top_cut"]
        self.leaderboard = db_connections["leaderboard"]
        self.region = db_connections["region"]
        
        # Tournament data cache
        self.tournament_json = None
        self.current_tournament_json = None
        
    async def start_monitoring(self):
        """Start monitoring a tournament until it's finalized"""
        logger.info(f"Starting monitoring for tournament ID: {self.tournament_id}")
        
        # Initialize API calls
        username = self.config['challonge_api']['username']
        api_key = self.config['challonge_api']['key']
        self.calls_instance = calls.calls(username, api_key)
        
        # Load tournament data from JSON if needed
        self._load_tournament_json()
        
        # Check finalized status from DB
        finalized_status = self.modif_tournament.get_finalized_status(self.tournament_id)
        if finalized_status == 1:
            logger.info(f"Tournament {self.tournament_id} is already finalized. Skipping monitoring.")
            return
            
        # Begin monitoring loop
        await self._monitor_loop()
        
    async def stop(self):
        """Signal the monitor to stop"""
        logger.info(f"Stopping monitor for tournament {self.tournament_id}")
        self.stop_monitor = True
        # No need to return an awaitable
        return
    
    async def _monitor_loop(self):
        """Main monitoring loop for a tournament"""
        previous_data = None
        previous_data_participants = None
        last_check = False
        interval = self.config['challonge_api']['interval']
        slower_check_interval = 60 * 60 * 3  # 3 hours in seconds
        
        while not self.stop_monitor:
            try:
                logger.info(f"Checking tournament {self.tournament_id}...")
                
                # Get tournament data from API
                tournament_data = self.calls_instance.get_tournament(self.tournament_id)
                if not tournament_data:
                    logger.error(f"Failed to get tournament data for {self.tournament_id}")
                    await asyncio.sleep(interval)
                    continue
                    
                logger.info(f"Tournament {self.tournament_id} state: {tournament_data['state']}")
                
                # Determine check interval based on tournament state
                if tournament_data['state'] in ['underway', 'group_stages_underway', 'final_stage_underway']:
                    # Tournament is active, use normal interval from config
                    interval = self.config['challonge_api']['interval']
                    if self.last_state not in ['underway', 'group_stages_underway', 'final_stage_underway']:
                        logger.info(f"Tournament {self.tournament_id} is now active. Using shorter interval: {interval}s")
                elif tournament_data['state'] in ['complete', 'awaiting_review']:
                    # Tournament is complete, process final data
                    last_check = True
                    logger.info(f"Tournament {self.tournament_id} is complete. Processing final data.")
                else:
                    # Tournament not yet active, use slower check interval
                    interval = slower_check_interval
                    if self.last_state != tournament_data['state']:
                        logger.info(f"Tournament {self.tournament_id} is not active. Using longer interval: {interval}s")
                
                # Save current state
                self.last_state = tournament_data['state']
                
                # Process tournament data
                if previous_data is None:
                    # First run processing
                    await self._initial_data_processing(tournament_data)
                    previous_data = tournament_data
                    previous_data_participants = self.calls_instance.get_participants(self.tournament_id)
                else:
                    # Regular update processing
                    participants = self.calls_instance.get_participants(self.tournament_id)
                    await self._process_tournament_updates(
                        tournament_data, 
                        participants, 
                        previous_data, 
                        previous_data_participants,
                        last_check
                    )
                    previous_data = tournament_data
                    previous_data_participants = participants
                
                # If this was the last check, finalize tournament and exit loop
                if last_check:
                    await self._finalize_tournament()
                    break
                
                # Dynamic sleep interval based on tournament state
                countdown_interval = interval
                if countdown_interval > 60:  # Only show countdown for longer intervals
                    next_check_time = datetime.now() + timedelta(seconds=countdown_interval)
                    logger.info(f"Next check for tournament {self.tournament_id} at {next_check_time}")
                    await asyncio.sleep(countdown_interval)
                else:
                    # For shorter intervals, show countdown
                    while countdown_interval > 0 and not self.stop_monitor:
                        if countdown_interval % 10 == 0 or countdown_interval <= 5:
                            logger.debug(f"Next check in {countdown_interval} seconds")
                        await asyncio.sleep(1)
                        countdown_interval -= 1
                
            except Exception as e:
                logger.exception(f"Error monitoring tournament {self.tournament_id}: {e}")
                await asyncio.sleep(interval)  # Wait before retrying
    
    async def _initial_data_processing(self, tournament_data):
        """Process initial tournament data on first run"""
        logger.info(f"Initial data processing for tournament {self.tournament_id}")
        
        # Get participant data
        participant_count = tournament_data['participants_count']
        participants = self.calls_instance.get_participants(self.tournament_id)
        
        # Check if tournament exists in DB
        get_tournament = self.modif_tournament.get_tournament_by_url(self.tournament_id)
        is_new = True
        
        if get_tournament is not None:
            is_new = False
            tournament_db = get_tournament
        else:
            # Create new tournament
            tournament_db = self.modif_tournament.create_tournament(
                tournament_data['name'], 
                self.tournament_id, 
                participant_count, 
                self.region.get_region_id_by_name(self.config['tournament_data']['region'])[0]
            )

        # Process participants and matches
        if participant_count != tournament_db[3] or is_new:
            tournament_db = self.update_participant_count(tournament_db, participant_count)
            self.update_attendance_id(tournament_db)
            await self.check_participant_data(self.tournament_id, participants)
            logger.info(f"Participant count: {tournament_db[3]}")
            
        # Check match data if tournament is underway
        if tournament_data['state'] in ['underway', 'group_stages_underway', 'final_stage_underway'] or is_new:
            await self.check_match_data(self.tournament_id)
    
    async def _process_tournament_updates(self, tournament_data, participants, previous_data, previous_participants, last_check):
        """Process tournament updates during regular monitoring"""
        tournament_db = self._extract_first_item(self.modif_tournament.get_tournament_by_url(self.tournament_id))
        
        # Check for participant changes
        if (participants != previous_participants and tournament_data['state'] in ['pending', 'upcoming']) or last_check:
            if len(participants) == 0:
                logger.info("No participants found.")
            elif len(participants) != 0:
                if len(participants) != tournament_data['participants_count']:
                    participant_count = tournament_data['participants_count']
                    tournament_db = self.update_participant_count(tournament_db, participant_count)
                    self.update_attendance_id(tournament_db)
                    await self.check_participant_data(self.tournament_id, participants)
                    logger.info(f"Updated participant count: {tournament_db[3]}")
        
        # Check if tournament has entered group stages
        if tournament_data['state'] == 'group_stages_underway' and not self.is_two_stage:
            self.is_two_stage = True
            if self.current_tournament_json:
                self.current_tournament_json['is_two_stage'] = True
                self._save_tournament_json()
            
        # Check match data if tournament is active or during final check
        if tournament_data['state'] in ['underway', 'group_stages_underway', 'final_stage_underway'] or last_check:
            await self.check_match_data(self.tournament_id)
            
        # Check for players in final stage if needed
        if last_check or (self.is_two_stage and tournament_data['state'] == 'underway' and len(self.stage_two_participants) == 0):
            self.stage_two_participants = set_top_cut.get_finals_players(
                self.tournament_id, 
                self.calls_instance, 
                self.stage_two_participants,
                self.modif_tournament,
                self.modif_participants,
                self.modif_matches,
                self.modif_tournament_data
            )
    
    async def _finalize_tournament(self):
        """Process final tournament data and generate outputs"""
        logger.info(f"Finalizing tournament {self.tournament_id}")
        
        # Get tournament data from DB
        tournament = self.modif_tournament.get_tournament_by_url(self.tournament_id)
        
        # Calculate top cut if needed
        if tournament[7] == 0:
            logger.info("Calculating top cut...")
            set_top_cut.calculate_top_cut(
                self.config["tournament_data"]["is_store_championship"],
                tournament[0],
                self.calls_instance,
                self.modif_participants,
                self.modif_tournament,
                self.modif_tournament_data
            )
            
        # Generate CSV files
        date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        results = await self.generate_leaderboard_csv(tournament[0], tournament[5], "main_leaderboard.csv", date_time)
        logger.info("CSV files generated successfully")
        
        # Call WIX API if configured
        if (self.config['wix_api']['key'] is not None and 
            self.config['wix_api']['site_id'] is not None and 
            self.config['wix_api']['account_id'] is not None):
            
            import utils.wix_calls.wix_api as wix_api
            logger.info("Making Wix API call.")
            wix_api.call(
                date_time,
                self.config,
                self.config['wix_api']['key'],
                self.config['wix_api']['site_id'],
                self.config['wix_api']['account_id'],
                results,
                tournament[1],
                self.region.get_region_by_id(tournament[5]),
                tournament[4]
            )
        else:
            logger.info("Wix API not configured. Skipping Wix API call.")
    
    def update_participant_count(self, db, participant_count):
        """Update participant count in DB"""
        logger.info(f"Updating participant count from {db[3]} to {participant_count}")
        return self.modif_tournament.update_participant_count(db[0], participant_count)
    
    def update_attendance_id(self, db):
        """Update attendance ID based on participant count"""
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
    
    async def check_participant_data(self, tournament_id, participants):
        """Check and update participant data"""
        for p in participants:
            logger.debug(f"Processing participant {p['name']}")
            
            # Try to find player in DB
            player_db = None
            if p['username'] is not None:
                player_db = self.modif_players.get_player_by_username(p['username'])
            elif p['name'] is not None:
                player_db = self.modif_players.get_player_by_name(p['name'])
            
            # Create player if not found
            if player_db is None:
                from classes.player import player
                _player = player(p['name'], p['username'])
                player_db = self.modif_players.create_player(
                    _player.name, 
                    _player.username, 
                    self.config['tournament_data']['region']
                )
                if player_db is None:
                    logger.error(f"Failed to create player: {p['name']}")
                    continue
            
            # Get tournament ID from DB and add participant
            t_id = self.modif_tournament.get_tournament_by_url(tournament_id)[0]
            
            from classes.participant import participant
            if len(p['group_player_ids']) > 0:
                _participant = participant(player_db[0], t_id, p['id'], p['group_player_ids'][0])
            else:
                _participant = participant(player_db[0], t_id, p['id'])
                
            self.modif_participants.create_participant(
                _participant.tournament_id,
                _participant.player_db_id,
                _participant.player_id,
                _participant.group_id
            )
            
            # Initialize tournament data for player if needed
            if self.modif_tournament_data.get_data(t_id, player_db[0]) is None:
                self.modif_tournament_data.add_data(t_id, player_db[0])
        
        # Check for removed players
        db_participants = self.modif_participants.get_participants_by_tournament_id(tournament_id)
        for p in db_participants:
            found = False
            for p2 in participants:
                if p[3] == p2['id']:
                    found = True
                    break
            if not found:
                self.modif_participants.delete_participant(p[0])
                logger.info(f"Participant {p[0]} has been removed from tournament.")
    
    async def check_match_data(self, tournament_id):
        """Check and update match data"""
        matches = self.calls_instance.get_matches(tournament_id)
        
        # Get tournament from DB
        tournament_db =  self.modif_tournament.get_tournament_by_url(tournament_id)
        if tournament_db is None:
            logger.error(f"Tournament {tournament_id} not found in database.")
            return
        
        logger.info(f"Processing {len(matches)} matches")
        
        for m in matches:
            match_db = self.modif_matches.get_match_by_id(m['id'])
            
            # Add new match if not found
            if match_db is None:
                if m['player1_id'] is None and m['player2_id'] is None:
                    logger.debug(f"Skipping match {m['id']}: no player IDs")
                    continue
                    
                match_db = self.modif_matches.add_match(
                    m['id'],
                    m['round'],
                    m['player1_id'],
                    m['player2_id'],
                    tournament_db[0]
                )
                
                if match_db is None:
                    logger.error(f"Failed to add match {m['id']}")
                    continue
            else:
                # Update player IDs if needed
                if m['player1_id'] is not None and match_db[1] is None:
                    match_db = self.modif_matches.set_player1_id(match_db[5], match_db[0], m['player1_id'])
                
                if m['player2_id'] is not None and match_db[2] is None:
                    match_db = self.modif_matches.set_player2_id(match_db[5], match_db[0], m['player2_id'])
            
            # Set match to final if applicable
            if (self.modif_participants.get_participant_by_id_tournament_id(m['player1_id'], tournament_db[0]) is not None or
                self.modif_participants.get_participant_by_id_tournament_id(m['player2_id'], tournament_db[0]) is not None):
                self.modif_matches.set_match_to_final(match_db[7])
            
            # Process winner/loser if applicable
            if match_db[3] is None and match_db[4] is None:
                if m['winner_id'] is not None:
                    winner_player = self.modif_participants.get_participant_by_player_id_tournament_id(m['winner_id'], tournament_db[0])
                    loser_player = self.modif_participants.get_participant_by_player_id_tournament_id(m['loser_id'], tournament_db[0])
                    
                    if winner_player and loser_player:
                        winner_player = winner_player[0]
                        loser_player = loser_player[0]
                        
                        match_db = self.modif_matches.update_match_winner(
                            match_db[0],
                            m['winner_id'],
                            m['loser_id'],
                            m['scores_csv']
                        )
                        
                        self.modif_tournament_data.add_win(tournament_db[0], winner_player[1])
                        self.modif_tournament_data.add_loss(tournament_db[0], loser_player[1])
            
            # Handle match reset if needed
            elif m['winner_id'] is None and match_db[3] is not None:
                winner_player_id = match_db[3]
                loser_player_id = match_db[4]
                
                self.modif_tournament_data.remove_win(tournament_db[0], winner_player_id)
                self.modif_tournament_data.remove_loss(tournament_db[0], loser_player_id)
                self.modif_matches.undo_match_winner(match_db[0])
    
    async def generate_leaderboard_csv(self, tournament_id, region, filename, date_time):
        """Generate leaderboard CSV files"""
        results = []
        
        # Append main board
        results.append([self.leaderboard.get_main_board()])
        
        # Generate main leaderboard CSV
        headers = ["Rank", "Username", "Total Points", "Win Percentage", "Region"]
        with open(filename, 'w', newline='') as csvfile:
            import csv
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            for data in results[0]:
                for row in data:
                    csvwriter.writerow(list(row))
        
        logger.info(f"Generated main leaderboard CSV: {filename}")
        
        # Generate tournament-specific leaderboard
        tournament = self.modif_tournament.get_tournament_by_id(tournament_id)
        results.append([self.leaderboard.get_tournament_leaderboard(tournament_id)])
        
        tournament_name = tournament[1].replace("/", "_").replace(" ", "_")
        filename = f"{tournament_name}_{date_time}_leaderboard.csv"
        
        # Remove file if it exists
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        
        # Generate tournament leaderboard CSV
        with open(filename, 'w', newline='') as csvfile:
            import csv
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            
            if self.config['tournament_data']['is_store_championship'] == 0:
                for data in results[0]:
                    for row in data:
                        csvwriter.writerow(list(row))
            else:
                for data in results[1]:
                    for row in data:
                        csvwriter.writerow(list(row))
        
        logger.info(f"Generated tournament leaderboard CSV: {filename}")
        return results
    
    def _load_tournament_json(self):
        """Load tournament data from JSON file"""
        if not os.path.exists('config/tournament_data.json'):
            with open('config/tournament_data.json', 'w') as f:
                f.write('{}')
                
        with open('config/tournament_data.json') as f:
            self.tournament_json = json.load(f)
            
        for t in self.tournament_json:
            if t[0] == self.tournament_id:
                self.current_tournament_json = t
                break
    
    def _save_tournament_json(self):
        """Save tournament data to JSON file"""
        if self.tournament_json and self.current_tournament_json:
            with open('config/tournament_data.json', 'w') as f:
                json.dump(self.tournament_json, f, indent=4)

    def _extract_first_item(self, result):
        if isinstance(result, tuple) and len(result) > 0:
            return result[0]
        return result