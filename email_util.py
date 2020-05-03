import config
from datetime import datetime
from socket import gethostname
import smtplib
from email.message import EmailMessage

def send_email(message_body):
  send_gmail(create_message(message_body))

def send_gmail(message):
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login(config.gmail_id, config.gmail_app_password)
  s.send_message(message)
  s.quit()

def create_message(message_body):
  message = EmailMessage()
  message.set_content(message_body)
  message['Subject'] = 'Restic Backup on ' + gethostname() + ' at ' + datetime.now().ctime()
  message['From'] = config.gmail_id
  message['To'] = config.send_to
  return message
