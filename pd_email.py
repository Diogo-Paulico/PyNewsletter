import email, smtplib, ssl, datetime, sys, imaplib, email.header
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


emailBodyFile = open(TEXT_BODY_FILE,'r')

body = emailBodyFile.read()


def removeSubscriber(email):
    print (email)
    global df
    count = df.Email.count()
    df = df[df.Email != email]
    df.Email.to_csv(CSV_FILE, index = False)
    return (df.Email.count() != count)


def getUnsubscribers():
    
    emailsToRemove=[]
    
    M = imaplib.IMAP4_SSL(IMAP_ADRESS)

    try:
        rv, data = M.login(SENDER_EMAIL, PASSWORD)
    except imaplib.IMAP4.error:
        print ("LOGIN FAILED!!! ")
        sys.exit(1)

    rv, data = M.select(EMAIL_FOLDER)
    if rv != 'OK':
        M.logout()
        return
    
    rv, data = M.search(None, '(UNSEEN SUBJECT "{0}")'.format(CANCEL_SUBJECT_KEYWORD))
    if rv != 'OK' or str(data[0]) == "b''":
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num) 
            return

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        emailFrom = str(email.utils.parseaddr(msg['From'])[1])
        emailsToRemove.append(emailFrom.strip())
    M.close()
    M.logout()
    return emailsToRemove


def unsubHandler():
    count = 0
    toUnsub = getUnsubscribers()
    emailingListChanged = False
    if toUnsub:
        for email in toUnsub:
            emailingListChanged = removeSubscriber(email)
            count += 1
        print('Removed %d subscribers' % (count)) 
    else:
        print('No subscribers removed')
    return emailingListChanged



def messageBuilder(email_receiver):
        message = MIMEMultipart()
        message["From"] = SENDER_NAME
        message["To"] = email_receiver
        message["Subject"] = SUBJECT

        message.attach(MIMEText(body, "plain"))
        return message.as_string()

def newsletterSend():
    contacts = buildContacts()
    unsubHandler()
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

newsletterSend()