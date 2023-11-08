from services.db_connection import connect
from secrets import token_hex
from argon2 import PasswordHasher
from datetime import datetime, timedelta

def getAuthToken(userID):
    """
    This method generates and stores an authorisation token for a given user,
    returning the plaintext token to be stored by the client.
    """
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Generate the plaintext and hashed token
                plaintext, hash_token = generateToken()
                
                # Calculate token expiry
                expiry = datetime.now() + timedelta(days=7)
                
                # Insert hashed token into the database
                sql = "INSERT INTO AuthToken (userID, tokenHash, expiry) VALUES (%s, %s, %s);"
                
                try:
                    cursor.execute(sql, (userID, hash_token, expiry))
                    connection.commit()
                except Exception as e:
                    # An error has occurred while inserting, revert changes
                    connection.rollback()
                    return (None, str(e))
                
                # Inserted to database successfully, return plaintext token without error
                return(plaintext, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])
    
    
def generateToken():
    """
    This method generates a random authorisation token and returns it in both
    plaintext and hashed form.
    """
    # Generate random plaintext token
    plaintext = token_hex(16)
    
    # Hash the token
    hasher = PasswordHasher()
    hash_token = hasher.hash(plaintext)
    
    # Return both tokens
    return plaintext, hash_token