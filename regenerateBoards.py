import csv
import json
import os
import utils.wix_calls.wix_api as wix_api
import utils.db_operations.initDB as initDB
import utils.db_operations.leaderboard as leaderboard
import utils.db_operations.tournament as tournament
import utils.db_operations.region as region
import utils.misc as misc
def regenerate_boards():
    config = {}
    if os.path.exists('config/config.json'):
        with open('config/config.json') as f:
            config = json.load(f)
    else:
        print("Check that config file exists within conifg folder.")
        raise FileNotFoundError("Config file not found.")
     
    db = initDB.initDB('config/config.json').get_connection()
    lb = leaderboard.leaderboard(db)
    tb = tournament.tournament(db)
    rb = region.region(db)

    tournament_id = misc.extract_tournament_id(config['challonge_api']['tournament_url'])
    t = tb.get_tournament_by_url(tournament_id)

    cursor = db.cursor()

    results = []
        
    results.append([lb.get_main_board()])
    
        # Define the CSV headers
    headers = [
            "Rank", "Username", "Total Points" "Win Percentage", "Region"
        ]
    
    filename = "main_leaderboard.csv"
        
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
        
        
    results.append([lb.get_tournament_leaderboard(tournament_id)])
        
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

        
    results.append([lb.get_region_leaderboard(t[5])])
        
    filename = f"{rb.get_region_by_id(t[5])[1]}_leaderboard.csv"
        
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

    wix_api.call(config, config['wix_api']['key'], config['wix_api']['site_id'], config['wix_api']['account_id'], results, t[1], rb.get_region_by_id(t[5]), t[5])
    

regenerate_boards()