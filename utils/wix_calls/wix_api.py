import json
import requests
from utils import misc


def call(config, api_key, site_id, account_id, data, tournament_name, region, is_side_event=False):
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "wix-account-id": account_id,
        "wix-site-id": site_id
    }
    if not is_side_event:
        create_main_board(headers, data[0], config['wix_collection']['main_board_id'] )
        create_regional_board(headers, data[1], region[1])
        
    create_tournament_board(headers, data[2], tournament_name)  
        
def create_main_board(headers, data, main_board_data):
    main_board_name = main_board_data.replace("_", " ")
    post_data = {
         "dataCollectionId": main_board_data
    }        
    current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
        
    if current_data.status_code == 200:
        data_item_ids = []
        for item in current_data.json()['dataItems']:
            data_item_ids.append(item['id'])
                
        delete_data_items(headers, data_item_ids, main_board_data, current_data, post_data)            
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
    else:     
        current_data = create_new_collection(headers, main_board_data, main_board_name)
    
    create_data_items(data, headers, main_board_data)

def create_regional_board(headers, data, region):
    board_id = f"{region.replace(' ', '_')}_Board"
    board_name = f"{region} Board"
    post_data = {
         "dataCollectionId": board_id
    }        
    current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
        
    if current_data.status_code == 200:
        data_item_ids = []
        for item in current_data.json()['dataItems']:
            data_item_ids.append(item['id'])
                
        delete_data_items(headers, data_item_ids, board_id,current_data, post_data)            
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
    else:     
        current_data = create_new_collection(headers, board_id, board_name)
    
    create_data_items(data, headers,board_id)
    
def create_tournament_board(headers, data, tournament_name):
    board_id = f"{tournament_name}_Board"
    board_name = f"{tournament_name} Board"
    post_data = {
        "dataCollectionId": board_id
    }        
    current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
        
    if current_data.status_code == 200:
        data_item_ids = []
        for item in current_data.json()['dataItems']:
            data_item_ids.append(item['id'])
                
        delete_data_items(headers, data_item_ids, board_id, current_data, post_data)            
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
    else:     
        current_data = create_new_collection(headers, board_id, board_name)
    
    create_data_items(data, headers, board_id)

def create_new_collection(headers, collection_id, collection_name):
    post_data = {
                 "collection": {
                    "id": collection_id,
                    "displayName": collection_name,
                    "fields":[
                        {
                            "key": "rank",
                            "displayName": "Rank",
                            "type": "NUMBER"
                        },
                        {
                            "key": "username",
                            "displayName": "Username",
                            "type": "TEXT"
                        },
                        {
                            "key": "total_points",
                            "displayName": "Points",
                            "type": "NUMBER"
                        },
                        {
                            "key": "win_percentage",
                            "displayName": "Win Percentage",
                            "type": "NUMBER"
                        },
                        {
                            "key": "region",
                            "displayName": "Region",
                            "type": "TEXT"
                        }
                    ]
                }   
            }
            
    new_board = requests.post("https://www.wixapis.com/wix-data/v2/collections", headers=headers, data=json.dumps(post_data))
    print(f"New Board: {new_board}")
    return requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))

def delete_data_items(headers, data_item_ids, board_id, current_data, post_data):
    data_item_ids = []
    for item in current_data.json()['dataItems']:
        data_item_ids.append(item['id'])
                
    while len(data_item_ids) > 0:
        delete_data = {
            "dataCollectionId": board_id,
            "dataItemIds": data_item_ids
        }
        del_req = requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/remove", headers=headers, data=json.dumps(delete_data))
        print(f"Delete Request: {del_req}")
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
        data_item_ids = []
        for item in current_data.json()['dataItems']:
            data_item_ids.append(item['id'])

def create_data_items(data, headers, board_id):
    data_items = []   
    for row in data:
        for r in row:    
            data_items.append({                    
                "data": {                    
                "rank": int(r[0]),
                "username": str(r[1]),
                "total_points": int(r[2]),
                "win_percentage": f"{float(r[3]) * 100}%",
                "region": str(r[4])
                    }
            })            
    post_data = {
        "dataCollectionId": board_id,
        "data_items": data_items,
    }
        
    print(f"Data Items: {data_items} Length: {len(data_items)}")
        
    requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/insert", headers=headers, data=json.dumps(post_data, cls=misc.DecimalEncoder))
