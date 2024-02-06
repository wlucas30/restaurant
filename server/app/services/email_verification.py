from services.db_connection import connect
from random import randint
from argon2 import PasswordHasher
from smtplib import SMTP, SMTPException
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# This function initiates the email verification process for a provided userID
# Return format is (Success (True or False), Error message (optional))
def beginVerification(userID):
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve the email address of the given userID
                sql = "SELECT email FROM User WHERE userID = %s;"
                cursor.execute(sql, (userID,))
                result = cursor.fetchone()
                
                if result is None:
                    # No user with the specified userID, error message
                    return (False, "No user was found with the provided userID")
                
                email = result[0]
                
                # Generate a random verification code
                plaintextCode = generateCode()
                
                # Hash the generated code for storing in the database
                hasher = PasswordHasher()
                hashedCode = hasher.hash(plaintextCode)
                
                # Calculate the expiry time for the verification code
                expiry = datetime.now() + timedelta(minutes=15)
                
                # Store the hashed code in the database
                try:
                    sql = "INSERT INTO VerificationCode (userID, codeHash, expiry) VALUES (%s, %s, %s);"
                    cursor.execute(sql, (userID, hashedCode, expiry))
                    connection.commit()
                except Exception as e:
                    connection.rollback() # revert changes
                    return (False, f"Error occurred during insertion: {e}")
                
                # Send the plaintext code to the provided email address
                emailed = emailCode(plaintextCode, email)
                if not emailed[0]:
                    # An error occurred, return the error message
                    return emailed
                else:
                    # No error has occurred, so return success message
                    return (True, None)
    else:
        # An error has occurred, return the error message
        return (False, connection[1])
    
# This function generates a random, 6-digit numeric code
def generateCode():
    code = ""
    for _ in range(6): # length of code
        code += str(randint(0, 9))
    return code
        
# This function sends an email containing the provided code to the provided address
def emailCode(code, email):
    # Retrieve email server password
    password = getEmailPassword()
    if password is None:
        return (False, "An error occurred retrieving the email server password")
    
    try:
        # Create a new message
        msg = EmailMessage()
        msg["From"] = "tableNest@outlook.com"
        msg["To"] = email # we assume this is already validated as it is stored in db
        msg["Subject"] = "tableNest Verification Code"
        msg.add_alternative("""
        This is your verfication code to sign in to tableNest.<br>
        <b>%s</b><br>
        If you did not request this, you do not need to take any action.
        """ % (code), subtype="html")
        
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