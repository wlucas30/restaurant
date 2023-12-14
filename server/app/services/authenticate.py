from services.db_connection import connect
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from models.user import User, ProfessionalUser

# This function checks whether a provided authentication token is valid
def authenticate(userID, token):
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve all stored, non-expired tokens for the provided userID
                sql = """
                SELECT
                    AuthToken.tokenHash
                FROM
                    AuthToken INNER JOIN USER
                        ON AuthToken.userID = User.userID
                WHERE
                    AuthToken.userID = %s
                    AND AuthToken.expiry > NOW()
                    AND User.loginAttempts <= 5;
                """
                cursor.execute(sql, (userID,))
                result = cursor.fetchall()
                
                # Initialise a PasswordHasher object for verifying hashes
                hasher = PasswordHasher()
                
                # We iterate through each valid stored token and check if it matches
                for row in result:
                    token_hash = row[0]
                    try:
                        if hasher.verify(bytes(token_hash), str(token)):
                            # A matching token has been found, reset login attempts
                            sql = "UPDATE User SET loginAttempts = 0 WHERE userID = %s;"
                            try:
                                cursor.execute(sql, (userID,))
                                connection.commit()
                            except Exception as e:
                                # An error has occurred, revert changes
                                connection.rollback()
                                return (False, str(e))
                            
                            # Return authentication success message
                            return (True, None)
                    except VerifyMismatchError:
                        continue
                
                # No matching token has been found, increment login attempts
                sql = "UPDATE User SET loginAttempts = loginAttempts + 1 WHERE userID = %s;"
                
                try:
                    cursor.execute(sql, (userID,))
                    connection.commit()
                except Exception as e:
                    # An error has occurred, revert changes
                    connection.rollback()
                    return (False, str(e))
                
                # Return authentication failure error
                return (False, "The provided authentication token is invalid or expired")
    else:
        # An error has occurred, return the error message
        return (False, connection[1])

# This function authenticates professional users and returns their restaurantID
def authenticateProfessional(userID, token):
    """# First authenticate the provided token
    authentication = authenticate(userID, token)
    if not authentication[0]:
        # The authentication failed, return the error
        return (None, authentication[1])"""

    # Check that the user is a professional
    user = User(userID=userID)
    if not user.professional:
        # The user is not a professional, return an error
        return (None, "The user is not a professional")

    # The user is a professional, so find their restaurantID
    user = ProfessionalUser(userID)
    restaurantID = user.restaurantID

    # Return the restaurantID
    return (restaurantID, None)