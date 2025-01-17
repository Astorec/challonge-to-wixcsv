import json
import requests
from utils import misc


def call(config, api_key, site_id, account_id, data, tournament_name, region_id, region, is_side_event=False):
        headers= {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "wix-account-id": account_id,
            "wix-site-id": site_id
        }
        
        if not is_side_event:
            post_data = {
                "dataCollectionId": config['wix_collection']['main_board_id']
            }
            
            current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
            
            if current_data.status_code == 200:
                print("Got the view data")
                
            data_item_ids = []
            
            for item in current_data.json()['dataItems']:
                data_item_ids.append(item['id'])
            
            if len(data_item_ids) > 0:
                delete_data = {
                    "dataCollectionId": config['wix_collection']['main_board_id'],
                    "dataItemIds": data_item_ids
                }
                requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/remove", headers=headers, data=json.dumps(delete_data))
            
            data_items = []
            
            for row in data[0]:
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
            
            requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/insert", headers=headers, data=json.dumps(post_data, cls=misc.DecimalEncoder))
            
            
            # Check to see if we have a collection already made for the region
            region_name = region.get_region_by_id(region_id)[1]
            
            post_data = {
                "dataCollectionId": region_name
            }
            
            current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
            r_id = region_name.replace(" ", "-")
            if current_data.status_code == 200:
                print("Got the view data")
            else:
                # Create the id by removing spaces and replacing with dashes
        
                # Create the collection
                post_data = {
                    "collection": {
                        "id": r_id,
                        "name": region_name,
                    }
                }
                
                current_data = requests.post("https://www.wixapis.com/wix-data/v2/collections", headers=headers, data=json.dumps(post_data))
            
            data_item_ids = []
        
            for item in current_data.json()['dataItems']:
                data_item_ids.append(item['id'])
            
            if len(data_item_ids) > 0:
                delete_data = {
                    "dataCollectionId": r_id,
                    "dataItemIds": data_item_ids
                }
                requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/remove", headers=headers, data=json.dumps(delete_data))
            
            data_items = []
            
            print(f"Data: {data[2]}")
            for row in data[2]:
                data_items.append({
                    "data": {
                        "rank": row[0],
                        "username": row[1],
                        "total_points": row[2]
                    }
                })
                
            post_data = {
                "dataCollectionId": r_id,
                "dataItems": data_items
            }
        
            print(f"Data Items: {data_items}")
            requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/insert", headers=headers, data=json.dumps(post_data, cls=misc.DecimalEncoder))
            
            
        # Check to see if we have a collection already made for the tournament name
        post_data = {
            "dataCollectionId": tournament_name
        }
        
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
        
        if current_data.status_code == 404:
            print("Creating new collection")
            post_data = {
                "collection": {
                    "id": tournament_name,
                    "name": tournament_name,
                }
            }
            
            current_data = requests.post("https://www.wixapis.com/wix-data/v2/collections", headers=headers, data=json.dumps(post_data))
        
        # Create the id by removing spaces and replacing with dashes
        t_id = tournament_name.replace(" ", "-")
            
        if current_data.status_code == 200:
            print("Got the view data")
        
        data_item_ids = []
        
        for item in current_data.json()['dataItems']:
            data_item_ids.append(item['id'])
        
        if len(data_item_ids) > 0:
            delete_data = {
                "dataCollectionId": t_id,
                "dataItemIds": data_item_ids
            }
            requests.post("https://www.wixapis.com/wix-data/v2/bulk/items/remove", headers=headers, data=json.dumps(delete_data))
            
        data_items = []
        
        for row in data[1]:
            data_items.append({
                "data": {
                    "rank": row[0],
                    "username": row[1],
                    "total_points": row[2]
                }
            })
            
        post_data = {
            "dataCollectionId": t_id,
            "dataItems": data_items
        }
        
        print(f"Data Items: {data_items}")
        
        current_data = requests.post("https://www.wixapis.com/wix-data/v2/items/query", headers=headers, data=json.dumps(post_data))
