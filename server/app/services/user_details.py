from services.db_connection import connect
from services.authenticate import authenticate

# This function provides details about a specified userID
def getAccountDetails(userID, auth_token):
    # Check if the provided token is valid
    authentication = authenticate(userID, auth_token)
    if not authentication[0]:
        # Authentication failed
        return (None, authentication[1])
    
    # Authentication succeeded, attempt to connect to the database
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                sql = "SELECT name, email, professional FROM User WHERE userID = %s;"
                cursor.execute(sql, (userID,))
                result = cursor.fetchone()
                
                if result is None:
                    # No user exists with the provided userID
                    return (None, "No user with the given userID was found")
                
                # Organise the user details into a dictionary for easy access
                user_details = {
                    "name": result[0],
                    "email": result[1],
                    "professional": result[2] == 1 #converts 1/0 to True/False
                }
                
                # Return the details with no error
                return (user_details, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])