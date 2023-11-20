from services.db_connection import connect
import datetime

# This function returns a list of all available reservation start times
def getAvailableReservations(restaurantID, date, persons):
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve all opening periods on the selected date
                openingPeriods = getOpeningPeriods(cursor, restaurantID, date)
                availableStartTimes = []
                
                # Iterate through each OpeningPeriod
                for period in openingPeriods:
                    currentTime, closingTime = period
                    
                    # Check each 30 minute period up to 2 hours before closing
                    closingTime -= datetime.timedelta(hours=2)
                    
                    while currentTime <= closingTime and currentTime > datetime.datetime.now():
                        # Check availability at this time
                        currentDatetime = datetime.datetime.combine(date, datetime.time(0,0)) + currentTime
                        sql = """
                        SELECT tableID FROM RestaurantTable
                        WHERE restaurantID = %s
                        AND capacity >= %s
                        AND tableID NOT IN (
                            SELECT tableID FROM Reservation
                            WHERE
                                restaurantID = %s
                                AND ABS(TIMESTAMPDIFF(SECOND, %s, DATETIME)) < 7200
                        );
                        """
                        cursor.execute(sql, (restaurantID, persons, restaurantID, currentDatetime))
                        result = cursor.fetchall()
                        
                        if len(result) > 0:
                            # This means there is availability in the selected period
                            # Convert the start time to string format and add it
                            currentTimeStr = (datetime.datetime.min + currentTime).strftime("%H:%M")
                            
                            availableStartTimes.append(currentTimeStr)
                        
                        # Add 30 minutes and check next time slot
                        currentTime += datetime.timedelta(minutes=30)
                
                return (availableStartTimes, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])
    
# This function retrieves all stored OpeningPeriods for a restaurant
def getOpeningPeriods(cursor, restaurantID, date):
    # Prepare an empty array for storing these opening periods
    openingPeriods = []
    
    # Convert the date to a day as a number (1=Monday)
    dayOfWeek = date.weekday() + 1
    
    # Retrieve OpeningPeriods
    sql = """
    SELECT openingTime, closingTime FROM OpeningPeriod
    WHERE restaurantID = %s AND dayOfWeek = %s;
    """
    cursor.execute(sql, (restaurantID, dayOfWeek))
    result = cursor.fetchall()
    
    # Iterate through each OpeningPeriod and append it to openingPeriods
    for period in result:
        openingPeriods.append((period[0], period[1]))
    
    return openingPeriods