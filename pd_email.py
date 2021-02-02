import email, smtplib, ssl, datetime, poplib
import pandas as pd

from config import *
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def buildContacts():
    global df
    df = pd.read_csv(CSV_FILE)
    contacts = df.Email
    return contacts


buildContacts()

emailBodyFile = open(TEXT_BODY_FILE,'r')

body = emailBodyFile.read()


def removeSubscriber(email):
    global df
    count = df.Email.count()
    df = df[df.Email != email]
    df.Email.to_csv('contactsFalse.csv', index = False)
    return (df.Email.count() != count)
    


def messageBuilder(email_receiver):
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = email_receiver
        message["Subject"] = SUBJECT

        message.attach(MIMEText(body, "plain"))
        return message.as_string()

def emailSend():
    contacts = buildContacts()
    counter = 0
    
    context = ssl.create_default_context() 
    with smtplib.SMTP_SSL(SMTP_ADRESS, SSL_PORT, context=context) as server:
            try: 
                server.login(SENDER_EMAIL, PASSWORD)
                for receiver_email in contacts:      
                    server.sendmail(SENDER_EMAIL, receiver_email, messageBuilder(receiver_email))
                    counter+=1
            except:
                print("SMTP server connection error")
        
    print('Sent ' + str(counter) + ' out of '+ str(contacts.size) + ' emails.')

print('yes')