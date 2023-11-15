from services.authenticate import authenticate
from services.db_connection import connect

# This function places a review for a given restaurant
def makeReview(userID, token, restaurantID, rating, title, body): 
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Validate the provided data
                try:
                    rating = int(rating)
                except ValueError:
                    return (False, "The provided argument for 'rating' is invalid")
                
                if rating < 1 or rating > 5:
                    return (False, "'rating' must be between 1 and 5")
                
                if len(title) > 50:
                    return (False, "Review title must not exceed 50 characters")
                
                # Authenticate user
                authentication = authenticate(userID, token)
                if not authentication[0]:
                    return (False, authentication[1]) # authentication failed
                
                # Check that the restaurant exists
                if not checkRestaurantExists(restaurantID, cursor):
                    return (False, "The provided restaurantID is not associated with any restaurant")
                
                # Insert new review into Review table
                sql = """
                INSERT INTO Review (restaurantID, userID, rating, title, body)
                VALUES (%s, %s, %s, %s, %s);
                """
                # Values are automatically escaped
                try:
                    cursor.execute(sql, (restaurantID, userID, rating, title, body))
                    connection.commit()
                except Exception as e:
                    # An error has occurred, revert changes
                    connection.rollback()
                    return (False, str(e))
                
                # Review successfully inserted
                return (True, None)
                
    else:
        # An error has occurred, return the error message
        return (False, connection[1])
    
def checkRestaurantExists(restaurantID, cursor):
    sql = "SELECT name FROM Restaurant WHERE restaurantID = %s;"
    cursor.execute(sql, (restaurantID,))
    cursor.fetchall()
    
    # Returns True if a restaurant exists with the provided restaurantID
    return cursor.rowcount > 0