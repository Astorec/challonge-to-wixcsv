from datetime import datetime
from decimal import Decimal
import json
from urllib.parse import urlparse


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
    

def extract_tournament_id(url):
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