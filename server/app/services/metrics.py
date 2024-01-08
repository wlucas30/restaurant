from services.db_connection import connect

# This function provides statistics about a restaurant
def getMetrics(restaurantID):
    # Attempt to connect to the database
    connection = connect()

    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                hourlyReservations = calculateHourlyReservations(cursor, restaurantID)
                hourlyWaitingTimes = calculateMeanWaitingTimes(cursor, restaurantID)

                # Return the statistics with no error message
                return ({"hourlyReservations":hourlyReservations,
                         "hourlyWaitingTimes":hourlyWaitingTimes}, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])

# This function calculates the number of reservations placed for each hour in the current day
def calculateHourlyReservations(cursor, restaurantID):
    # Retrieve all reservations placed today
    sql = "SELECT datetime FROM Reservation WHERE DATE(datetime) = CURDATE() AND restaurantID = %s;"
    cursor.execute(sql, (restaurantID,))
    result = cursor.fetchall()

    # Initialise an empty dictionary for storing the number of reservations placed in each hour
    hourlyReservations = {}

    # Iterate through each reservation and increment the corresponding hour when necessary
    for row in result:
        hour = row[0].hour
        try:
            hourlyReservations[hour] += 1
        except KeyError:
            # Initialise the number of reservations for the hour if it has not been initialised
            hourlyReservations[hour] = 1

    return hourlyReservations

# This function calculates the mean order waiting time for each hour
def calculateMeanWaitingTimes(cursor, restaurantID):
    # Retrieve all orders fulfilled today
    sql = "SELECT timeOrdered, timeFulfilled FROM FoodOrder WHERE DATE(timeFulfilled) = CURDATE() AND restaurantID = %s;"
    cursor.execute(sql, (restaurantID,))
    result = cursor.fetchall()

    # Initialise an empty dictionary for storing the total waiting time for each hour
    hourlyWaitingTimes = {}
    # Initialise an empty dictionary for storing the number of orders for each hour
    hourlyOrders = {}

    # Iterate through each order and calculate the waiting time
    for row in result:
        timeOrdered = row[0]
        timeFulfilled = row[1]

        # Calculate the waiting time in minutes
        waitingTime = (timeFulfilled - timeOrdered).seconds // 60

        # Increment the corresponding hour when necessary
        hour = timeOrdered.hour
        try:
            hourlyWaitingTimes[hour] += waitingTime
        except KeyError:
            # Initialise the waiting time for the hour if it has not been initialised
            hourlyWaitingTimes[hour] = waitingTime

        try:
            hourlyOrders[hour] += 1
        except KeyError:
            # Initialise the number of orders for the hour if it has not been initialised
            hourlyOrders[hour] = 1

    # Calculate mean waiting time for each hour by dividing the waiting time by the number of orders
    for hour in hourlyWaitingTimes:
        hourlyWaitingTimes[hour] /= hourlyOrders[hour]

    return hourlyWaitingTimes