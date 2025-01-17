import json
from imap_tools import MailBox, A


def check_for_confirmation_response(config, tournament_id):
    with MailBox(config['email']['iamp_address']).login(config['email']['email_send_from'], config['email']['password'], config['email']['folder']) as mailbox:
        for msg in mailbox.fetch(A(subject=f'Top 8 Confirmation {tournament_id}')): 
            try:
                # Extract the email body
                email_body = msg.text or msg.html or msg.body
                if email_body:
                    # Parse the email body as JSON
                    return json.loads(email_body)
                else:
                    print("No valid data found in the email body.")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from email: {e}")
            except Exception as e:
                print(f"Error processing email: {e}")
    return None