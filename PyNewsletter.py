import email, smtplib, ssl, sys, imaplib, email.header
import pandas as pd

from config import *
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Loads the csv file given by the CSV_FILE variable
# @return -> list of email addresses contained in the column Email
def buildContacts():
    global df
    df = pd.read_csv(CSV_FILE)
    contacts = df.Email
    return contacts

# Loads the email body from the TEXT_BODY_FILE
body = open(TEXT_BODY_FILE,'r').read()

# Removes the given email from the loaded CSV file containing the emails
# @return -> True is the emailing list changed, False otherwise
def removeSubscriber(email_to_remove):
    global df
    count = df.Email.count()
    df = df[df.Email != email_to_remove]
    df.Email.to_csv(CSV_FILE, index = False)
    return (df.Email.count() != count)


# will use the IMAP protocol to check the EMAIL_FOLDER for unseen messages with the subject given by CANCEL_SUBJECT_KEYWORD
# @return -> the list of emails to be removed
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

# will handle all the unsubcribing, getting the emails to unsubscribe using the getUnsubscribers() function
# and remove them using the removeSubscriber(email_to_remove) function
# @return -> list of email adresses removed from the mailing list
def unsubHandler():
    count = 0
    toUnsub = getUnsubscribers()
    unSubd = []
    emailingListChanged = False
    if toUnsub:
        for email in toUnsub:
            emailingListChanged = removeSubscriber(email)
            if emailingListChanged:
                count += 1
                unSubd.append(email)
        print('Removed %d subscribers' % (count)) 
    else:
        print('No subscribers removed')
    return unSubd


# builds the message object for the emails given the email adress of the receiver (email_receiver)
# @return -> message object "stringified"
def messageBuilder(email_receiver):
        message = MIMEMultipart()
        message["From"] = SENDER_NAME
        message["To"] = email_receiver
        message["Subject"] = SUBJECT

        message.attach(MIMEText(body, "plain"))
        return message.as_string()

# builds the message object for the unsubscribed emails given the email adress of the receiver (email_receiver) and the path to the file containing the 
# message to be sent to unsubscribers (UNSUB_BODY_FILE) 
# @return -> message object "stringified"
def unsubMessageBuilder(email_receiver):
        unsubBody = open(UNSUB_BODY_FILE,'r').read()
        message = MIMEMultipart()
        message["From"] = SENDER_NAME
        message["To"] = email_receiver
        message["Subject"] = UNSUB_MESSAGE_SUBJECT

        message.attach(MIMEText(unsubBody, "plain"))
        return message.as_string()

# Will import the email adresses, handle unsubscribing emails using the previously defined functions,
# then it will send the unsub message to emails that asked to be removed if SEND_UNSUB_MESSAGE is set to True 
# and the newsletter to the emails present in the emailing list
def pyNewsletter():
    contacts = buildContacts()
    unsubEmails = unsubHandler()
    contacts = buildContacts()
    counter = 0 
    context = ssl.create_default_context() 
    with smtplib.SMTP_SSL(SMTP_ADRESS, SSL_PORT, context=context) as server:
            try: 
                server.login(SENDER_EMAIL, PASSWORD)
                if unsubEmails and SEND_UNSUB_MESSAGE:
                    for unsubEmail in unsubEmails:
                        server.sendmail(SENDER_EMAIL, unsubEmail, unsubMessageBuilder(unsubEmail))

                for receiver_email in contacts:      
                    server.sendmail(SENDER_EMAIL, receiver_email, messageBuilder(receiver_email))
                    counter+=1
            except:
                print("SMTP server connection error")
        
    print('Sent ' + str(counter) + ' out of '+ str(contacts.size) + ' emails.')

pyNewsletter()