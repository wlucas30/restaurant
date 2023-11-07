from services.db_connection import connect
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# This function checks whether a provided email verification code is valid and not expired
def checkVerificationCode(userID, verification_code):
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve all hashed verification codes stored for the given userID
                sql = "SELECT codeHash FROM VerificationCode WHERE userID = %s AND expiry > NOW();"
                cursor.execute(sql, (userID,))
                result = cursor.fetchall()

                # Initialise a PasswordHasher object for verifying hashes
                hasher = PasswordHasher()
                
                # We iterate through each valid stored code and check if it matches
                for row in result:
                    code_hash = row[0]
                    try:
                        if hasher.verify(bytes(code_hash), str(verification_code)):
                            # A matching code has been found, return with no error
                            return (True, None)
                    except VerifyMismatchError:
                        continue
                    
                # No matching code has been found, return error
                return (False, "The provided code is invalid or expired")
                    
    else:
        # An error has occurred, return the error message
        return (False, connection[1])