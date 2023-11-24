from models.user import User
from services.db_connection import connect
from services.authenticate import authenticate

# This function changes the details for a given user's restaurant
def updateRestaurant(userID, authToken, restaurantName, description, category, location):
    """# Begin by authenticating the provided userID and token
    authentication = authenticate(userID, authToken)
    
    if not authentication[0]:
        # Authentication has failed, return the error message
        return (False, authentication[1])"""
    
    # Now check that the user is a professional and owns a restaurant
    user = User(userID=userID)
    if not user.professional:
        return (False, "The provided userID does not manage any restaurant")
    
    # Authentication has succeeded, now validate the data
    validation = checkDataValidity(restaurantName, description, category, location)
    if not validation[0]:
        # Data validation has failed, return the error message
        return (False, validation[1])
    
    # Validation succeeded, now attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Update the user's restaurant with the provided parameters
                sql = """
                UPDATE Restaurant
                SET name = %s, description = %s, category = %s, location = %s
                WHERE managerUserID = %s;
                """
                try:
                    cursor.execute(sql, (restaurantName, description, category, location, userID))
                    connection.commit()
                except Exception as e:
                    # Updating the restaurant failed, revert changes and return an error
                    connection.rollback()
                    return (False, str(e))
                
                # Update succeeded, return success message with no error
                return (True, None)

def checkDataValidity(restaurantName, description, category, location):
    for element in [restaurantName, description, category, location]:
        if type(element) != str:
            # Provided data must be of type string, return an error
            return (False, "The provided data is in an invalid format")
    if len(restaurantName) > 50:
        # Length cannot exceed 50 characters
        return (False, "The provided restaurantName must not exceed 50 characters")
    if len(category) > 50:
        # Length cannot exceed 50 characters
        return (False, "The provided category must not exceed 50 characters")
    
    # The provided location must be two decimals separated by a comma
    try:
        latitude, longitude = (float(x) for x in location.split(","))
    except ValueError:
        # This means that the location is incorrectly formatted
        return (False, "The provided location is incorrectly formatted")
    
    # So far all tests have passed, so the data is valid
    return (True, None)