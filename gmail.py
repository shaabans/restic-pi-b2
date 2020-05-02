import config
from datetime import datetime
from socket import gethostname
import smtplib
from email.message import EmailMessage

def send_email(message):
  msg = EmailMessage()
  msg.set_content(message)
  msg['Subject'] = 'Restic Backup on ' + gethostname() + ' at ' + datetime.now().ctime()
  msg['From'] = config.gmail_id
  msg['To'] = config.send_to

  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login(config.gmail_id, config.gmail_app_password)
  s.send_message(msg)
  s.quit()
