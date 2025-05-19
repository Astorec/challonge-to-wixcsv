from collections import OrderedDict
import json
import os

def calculate_top_cut(is_store_championship, tournament_id, calls_instance,  modif_participants, modif_tournament, modif_tournament_data):
        
        fresh_top_cut = True
        tournament_data = modif_tournament_data.get_tournament_data(tournament_id)
        
        # Sort tournament data by rank descending
        tournament_data.sort(key=lambda x: x[5], reverse=True)
        
        # Check to see if column 5 is not 0
        for i, row in enumerate(tournament_data):
            if row[5] != 0:
                fresh_top_cut = False
                break
        
        # This is to stop the app from calculating the top cut again if it has already been calculated.
        # Useful for when we are importing a tournament that wasn't already in the database.
        if fresh_top_cut:
            url = modif_tournament.get_tournament_by_id(tournament_id)[2]
            matches = calls_instance.get_matches(url)
            participants = modif_participants.get_participants_by_tournament_id(tournament_id)
            finals_matches = []
            top_cut_size = modif_tournament_data.get_top_cut_size(tournament_id)
            # Remove all matches that are not in the top cut
            for m in matches:
                if m['group_id'] is None:
                    finals_matches.append(m)
    
            max_rounds = 0
            
            for m in finals_matches:
                if m['round'] > max_rounds:
                    max_rounds = m['round']

            placement = 0
            if max_rounds == 5:
                placement = 16
            elif max_rounds == 3:
                placement = 8
            elif max_rounds == 2:
                if participants.__len__() <= 8:
                    placement = 1
                elif participants.__len__() <= 16:
                    placement = 2
                else:
                    placement = 4
            
            for m in finals_matches:
                if m['round'] == 0:
                    # get player_id from winner_id
                    winner_id = modif_participants.get_participant_by_player_id_tournament_id( m['winner_id'],tournament_id)[0][1]
                    loser_id = modif_participants.get_participant_by_player_id_tournament_id(m['loser_id'],tournament_id)[0][1]
                    modif_tournament_data.add_placement(tournament_id, winner_id, 3)
                    modif_tournament_data.add_placement(tournament_id, loser_id, 4)  
                    modif_tournament_data.update_score_for_top_cut(tournament_id, winner_id, is_store_championship)
                    modif_tournament_data.update_score_for_top_cut(tournament_id, loser_id, is_store_championship)
                    break
            
            # Sort finals matches by round
            finals_matches.sort(key=lambda x: x['round'])
            placement_copy = placement
            # Loop max_rounds times
            for i in range(max_rounds):
                # Get all matches with the current round
                current_round_matches = [m for m in finals_matches if m['round'] == i + 1]
                # Get the players from the matches
                
                for m in current_round_matches:
                    winner_id = modif_participants.get_participant_by_player_id_tournament_id(m['winner_id'], tournament_id)[0][1]         
                    loser_id = modif_participants.get_participant_by_player_id_tournament_id(m['loser_id'], tournament_id)[0][1]
                                        
                    
                    # Check if we are in finals
                    if i + 1 == max_rounds:       
                        
                        modif_tournament_data.add_placement(tournament_id, winner_id, 1)   
                        modif_tournament_data.add_placement(tournament_id, loser_id, 2)
                        modif_tournament_data.update_score_for_top_cut(tournament_id, winner_id, is_store_championship)
                        modif_tournament_data.update_score_for_top_cut(tournament_id, loser_id, is_store_championship)
                    elif i + 1 == max_rounds - 1:
                        continue
                    else:                        
                        modif_tournament_data.add_placement(tournament_id, loser_id, placement_copy, is_store_championship )

                        if placement_copy <= top_cut_size:
                            modif_tournament_data.update_score_for_top_cut(tournament_id, loser_id, is_store_championship)
                        placement_copy -= 1

            calculate_rest_of_rankings(tournament_id, modif_tournament_data, placement, is_store_championship)            
            for p in participants:            
                modif_tournament_data.update_win_percentage(tournament_id, p[1])
                
                
        modif_tournament.set_finalized(tournament_id)
    
def calculate_rest_of_rankings(tournament_id, modif_tournament_data, placement, is_store_championship):
    all_players = modif_tournament_data.get_all_players_with_scores(tournament_id)
    all_players.sort(key=lambda x: x[3], reverse=True)
    
    previous_score = None
    for i, player in enumerate(all_players):
        player = list(player)
        if player[5] == 0:
                placement += 1
                modif_tournament_data.add_placement(tournament_id, player[2], placement, is_store_championship)                
        else:
            continue
    
 
def check_player_exists(player_id, participants):
    for participant in participants:
        if participant[3] == player_id:
            return True

def get_finals_players(tournament_id, calls_instance, stage_two_participants, modif_tournament, modif_participants, modif_matches, modif_tournament_data):
   
    # Get all unplayed matches and get the players from those matches
    matches = calls_instance.get_matches(tournament_id)
    
    # Find the highest round number in the finals matches
    highest_round = 0
    for m in matches:
        if m['group_id'] is None and m['round'] > highest_round:
            highest_round = m['round']

        
    tournament_db = modif_tournament.get_tournament_by_url(tournament_id)
    if not tournament_db:
        print(f"Tournament with ID {tournament_id} not found in DB.")
        return
    
    tournament_id = tournament_db[0]
    
    participants = modif_participants.get_participants_by_tournament_id(tournament_id)
    
                
    placement = 0
    if highest_round == 5:
        placement = 16
    elif highest_round == 3:
        placement = 8
    elif highest_round == 2:
        if participants.__len__() <= 8:
            placement = 1
        elif participants.__len__() <= 16:
            placement = 2
        else:
            placement = 4
    
    
    finals_matches = []
    
    for m in matches:
            player1_exists = check_player_exists(m['player1_id'], participants)
            player2_exists = check_player_exists(m['player2_id'], participants)
            
            if not player1_exists or not player2_exists:
                print(f"Error: Player ID {m['player1_id']} or {m['player2_id']} does not exist in participants. Skipping match ID {m['id']}.")
                continue
            
            # Proceed with your existing logic
            match = modif_matches.get_match_by_id(m['id'])
            if match is None:
                match = modif_matches.add_match(m['id'], m['round'], m['player1_id'], m['player2_id'], tournament_id)
                print(match)
                    
            if m not in finals_matches:
                finals_matches.append(m)
    if len(finals_matches) == 0:
        print("No pending matches found.")
        return
                
    return get_players(finals_matches, tournament_id, modif_participants)

def get_finals(tournament_id, modif_matches, modif_participants, modif_tournaments, calls_instance):
    matches = modif_matches.get_finals_matches(tournament_id)
    
    if matches.__len__() == 0 or matches is None:
        t = modif_tournaments.get_tournament_by_id(tournament_id)
        c_matches = calls_instance.get_matches(t[2])
        participants = modif_participants.get_participants_by_tournament_id(tournament_id)
        
        for m in c_matches:
            for p in participants:
                match = None
                if m['player1_id'] == p[3] or m['player2_id'] == p[3]:
                    match = modif_matches.add_match(m['id'], m['round'], m['player1_id'], m['player2_id'], tournament_id)
                if m['winner_id'] is not None and m['loser_id'] is not None and match is not None:
                    modif_matches.update_match_winner(match[0], m['winner_id'], m['loser_id'])
    
    return modif_matches.get_finals_matches(tournament_id)

def get_players(finals_matches, tournament_id, modif_participants):
    stage_two_participants = []
    
    # If finals_matches is a tuple convert it to a list
    if isinstance(finals_matches, tuple):
        finals_matches = list(finals_matches)
    
    for m in finals_matches:
        # get player 1 and 2 ids from the match
        if isinstance(m, dict):
            player1_id = m.get('player1_id')
            player2_id = m.get('player2_id')
        # Check if m is a tuple (e.g., from a database query)
        elif isinstance(m, tuple):
            player1_id = m[1]  # Assuming player1_id is at index 1
            player2_id = m[2]  # Assuming player2_id is at index 2
        else:
            continue
        
            # Get participant details
        participant1 = modif_participants.get_participant_by_player_id_tournament_id(player1_id, tournament_id)
        participant2 = modif_participants.get_participant_by_player_id_tournament_id(player2_id, tournament_id)
    
    
        # Add players to stage_two_participants if not already present
        if participant1:
            add_unique_participant(stage_two_participants, participant1)
        if participant2 :
            add_unique_participant(stage_two_participants, participant2)
    return stage_two_participants

def add_unique_participant(stage_two_participants, participant):
    player_id = participant[0][1]  # Assuming player_id is at index 1
    if player_id not in [p[0][1] for p in stage_two_participants]:
        stage_two_participants.append(participant)