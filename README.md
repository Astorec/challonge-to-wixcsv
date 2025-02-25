# Introduction
The goal of this project is to allow challonge boards to be automatically imported to WIX and also Extract them to a CSV file. It will send an e-mail out once the challonge tournament state is set to Compelte and will ask to 
confirm the top 8. Reply to the e-mail, change the subject to the requested subject heaer, copy the JSON, clear the body and paste the JSON in to the e-mail. The program will pull in the TOP 8 from the selection

Currently the application only does Top 8 and produces a Main board, but plan to add a feature to export the Main Board and the board for that specific tournament as well.


# Requirements
- MySQL
- Python3
- WIX Account with Access to the Studio of the Site
- Challonge Account and the API key
- ~~Email Account with SMTP and IAMP~~ To be Removed, this is no longer required.

# Setup

## Config.json
```json
{
    "db": {
      "host": "localhost",
      "user": "",
      "pass": "",
      "db": ""
    },
    "challonge_api":{
      "username": "",
      "key": "", 
      "tournament_url": "",
      "interval": 30
    },
    "tournament_data":{
      "region": "Scotland"
    },
    "wix_api":{
      "key": "",
      "site_id":"",
      "account_id": ""
    },
    "wix_collection":{
      "main_board_id": "Main_Board"
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

This has been setup based on another project I have been working on, but can be modified to how you need it. All the Data is grabbed and calculated based on the top cut data that is collected from a Challonge. Challonge needs to be configured so that that there are two rounds and a Tie Braker for 3rd place for this to work. 

Adding the Challonge link to the config will pull all the information from the API and load it into the DB when it runs. The interval is set for how often we check Challonge to stop it from being spammed.

The APP checks for the statge change of the rounds, when the group stages and finals are underway it will start checking for the Match Data on Challonge. Player data is stored on the DB and each player is given their own ID and is matched up to the TournamentData.
