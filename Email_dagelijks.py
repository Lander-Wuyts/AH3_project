###############
### IMPORTS ###
###############

import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import schedule                                 # pip install schedule
import time

#################
### VARIABLES ###
#################

# e-mail
message = """
Geachte,

In de bijlage kan u het document vinden met de overschot van deze week.

Met vriendelijke groeten
"""

send_mail_now = True
send_mail_time = "13:18"

sender = 'supermarkt.test@gmail.com'
password = '2ccs02AH3'
receiver = 'vzwsupermarkt.test@gmail.com'

reports_folder = 'Reports'

#####################
### CONFIGURATION ###
#####################

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = receiver
msg['Subject'] = 'Briefing'

current_date = datetime.now()

name = 'Rapport vervaldata - {}'.format(current_date.date())
pdfname = './{}/{}.pdf'.format(reports_folder, name)

#################
### FUNCTIONS ###
#################

def retrieve_pdf():
    # Global variables
    global pdfname
    global msg
    # Retrieve pdf and encode
    binary_pdf = open(pdfname, 'rb')

    payload = MIMEBase('application', 'octa-stream', Name=pdfname)
    payload.set_payload((binary_pdf).read())

    encoders.encode_base64(payload)
    # add header with pdf name
    payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)

    return payload


def construct_message():
    # Global variables
    global message
    # Building message for mail
    msg.attach(MIMEText(message, 'plain'))
    msg.attach(retrieve_pdf())
    
    return msg.as_string()


def send_mail():
    # Global variables
    global sender
    global password
    #use gmail with port
    session = smtplib.SMTP('smtp.gmail.com', 587)
    #enable security
    session.starttls()
    session.login(sender, password)
    # Message
    text = construct_message()

    # Send, quit and print feedback
    session.sendmail(sender, receiver, text)
    session.quit()
    print('Mail Sent')

#################
### EXECUTION ###
#################

# Sending a mail every day of the week at a certain time
schedule.every().monday.at(send_mail_time).do(send_mail)
schedule.every().tuesday.at(send_mail_time).do(send_mail)
schedule.every().wednesday.at(send_mail_time).do(send_mail)
schedule.every().thursday.at(send_mail_time).do(send_mail)
schedule.every().friday.at(send_mail_time).do(send_mail)

# Run code continuously
while True:
    schedule.run_pending()
    time.sleep(30)