from services.db_connection import connect
from services.authenticate import authenticate
from services.email import sendEmail
from datetime import datetime

# This function places a reservation for a table at a restaurant
def makeReservation(userID, authToken, restaurantID, date, time, persons):
    # Authenticate the provided token
    """authentication = authenticate(userID, authToken)
    if not authentication[0]:
        # Authentication failed, return an error
        return (None, authentication[1])"""
    
    # The provided date should be in format "YYYY-MM-DD"
    dateObject = None
    try:
        dateObject = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as e:
        # An error could occur if the provided date is incorrectly formatted
        return (False, str(e))
    
    # The provided time should be in the format "HH:MM", but must be at a 30-minute interval
    if time[-2:] not in ["00", "30"]:
        return (False, "The provided time must be at a 30-minute interval")
    
    # Attempt to combine the provided time with the date object
    try:
        timeObject = datetime.strptime(time, "%H:%M").time()
        dateObject = datetime.combine(dateObject, timeObject)
    except ValueError:
        # An error could occur if the provided time is incorrectly formatted
        return (False, "The provided time is incorrectly formatted")
    
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve the most optimal table to place a booking at
                tableID = getBestTableID(cursor, restaurantID, dateObject, persons)
                
                # Check if a tableID was found
                if tableID is None:
                    return (False, "No tables are available at the provided time")
                
                # A tableID was found, place a reservation
                sql = """
                INSERT INTO Reservation (restaurantID, tableID, userID, persons, datetime)
                VALUES (%s, %s, %s, %s, %s);
                """
                try:
                    cursor.execute(sql, (restaurantID, tableID, userID, persons, dateObject))
                    connection.commit()
                except Exception as e:
                    # An error has occurred while inserting, revert changes
                    connection.rollback()
                    return (False, str(e))
                
                # Send confirmation email
                sendConfirmationEmail(cursor, userID, restaurantID, date, time, persons)
                
                # Reservation has been made, return success
                return (True, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])

# This function returns the optimal table to make a booking at (least capacity)
def getBestTableID(cursor, restaurantID, dateObject, persons):
    sql = """
    SELECT
    	tableID
    FROM
    	RestaurantTable
    WHERE
    	restaurantID = %s
    	AND capacity >= %s
    	AND tableID NOT IN (
    		SELECT tableID FROM Reservation
    		WHERE
    			restaurantID = %s
    			AND ABS(TIMESTAMPDIFF(SECOND, %s, datetime)) <= 7200	
    	)
    ORDER BY capacity ASC;
    """
    cursor.execute(sql, (restaurantID, persons, restaurantID, dateObject))
    result = cursor.fetchall()
    if len(result) == 0:
        # There are no tables available at the provided time
        return None
    else:
        # Return the tableID from the first result
        return result[0][0]

# This function sends a confirmation email to confirm the reservation
def sendConfirmationEmail(cursor, userID, restaurantID, date, time, persons):
    # Retrieve the user's email address and name
    sql = "SELECT email, name FROM User WHERE userID = %s;"
    cursor.execute(sql, (userID,))
    emailAddress, userName = cursor.fetchone()
    
    # Retrieve the restaurant's name
    sql = "SELECT name FROM Restaurant WHERE restaurantID = %s;"
    cursor.execute(sql, (restaurantID,))
    restaurantName = cursor.fetchone()[0]
    
    # Send the email
    sendEmail(emailAddress, "Booking Confirmation", """
    Hi %s,<br>
    This is an email to confirm that you have placed a reservation at the restaurant
    <strong>%s</strong> on the date <strong>%s</strong> at <strong>%s</strong>,
    for <strong>%s person(s)</strong>.
    Thank you for using tableNest.
    """ % (userName, restaurantName, date, time, persons))