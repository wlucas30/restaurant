from smtplib import SMTP, SMTPException
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# This function sends an email from tableNest to the provided email address
def sendEmail(emailAddress, subject, body):
    # Retrieve email server password
    password = getEmailPassword()
    if password is None:
        return (False, "An error occurred retrieving the email server password")
    try:
        print("Sending message!")
        # Create a new message
        msg = EmailMessage()
        msg["From"] = "tableNest@outlook.com"
        msg["To"] = emailAddress
        msg["Subject"] = subject
        msg.add_alternative(body, subtype="html")
        
        # Establish connection with SMTP server
        server = SMTP("smtp.office365.com", 587)
        server.starttls() # enables secure SSL connection
        server.login("tableNest@outlook.com", password)
        
        # Send the message
        server.send_message(msg)
        
        # Close server connection
        server.quit()
        
        # Return success with no error message
        return (True, None)
    except SMTPException as e:
        # Return error message
        return (False, "Error occurred while sending email: "+str(e))
    
# This function retrieves the email server password securely from the environment
def getEmailPassword():
    # Initialise the environment variable from the .env file
    load_dotenv()
    
    password = None
    try:
        password = os.getenv("EMAIL_PASSWORD")
    except:
        # An error has occurred retrieving the password
        return None
    
    return password