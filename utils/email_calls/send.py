from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email(config, subject, body, to_email):
    from_email = config['email']['email_send_from']
    password = config['email']['password']

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(config['email']['smtp_address'], config['email']['smtp_port'])
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()