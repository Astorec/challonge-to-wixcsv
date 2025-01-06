# Introduction
The goal of this project is to allow challonge boards to be automatically imported to WIX and also Extract them to a CSV file. It will send an e-mail out once the challonge tournament state is set to Compelte and will ask to 
confirm the top 8. Reply to the e-mail, change the subject to the requested subject heaer, copy the JSON, clear the body and paste the JSON in to the e-mail. The program will pull in the TOP 8 from the selection

Currently the application only does Top 8 and produces a Main board, but plan to add a feature to export the Main Board and the board for that specific tournament as well.


# Requirements
- MySQL
- Python3
- WIX Account with Access to the Studio of the Site
- Challonge Account and the API key
- Email Account with SMTP and IAMP

# Setup

## Config.json
```json
{
    "db": {
      "host": "",
      "user": "",
      "pass": "",
      "db": ""
    },
    "challonge_api":{
      "username": "",
      "key": "", 
      "tournament_url": ""
    },
    "wix_api":{
      "key": "",
      "site_id":"",
      "account_id": ""
    },
    "wix_collection":{
      "collection_id": ""
    },
    "email":{
      "email_send_from": "",
      "email_send_to": "",
      "password": "",
      "smtp_address": "smtp.gmail.com",
      "smtp_port": 587,
      "iamp_address": "imap.gmail.com",
      "folder": "INBOX"
    }
  }
```

## TODO Add Setup instruction in relation to the above config


# Database Strucutre

This has been setup based on another project I have been working on, but can be modified to how you need it. All the Data is grabbed and calculated based on the Top 8 Data and points are caulcated on the Join of the tables.

## TODO Add Ability to select TOP 4
