from services.db_connection import connect
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

# This function estimates the time until the order is fulfilled using linear regression
def getOrderEta(foodOrderID):
    # Attempt to connect to the database
    connection = connect()

    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Check that the order is not already fulfilled
                sql = "SELECT timeFulfilled FROM FoodOrder WHERE foodOrderID = %s;"
                cursor.execute(sql, (foodOrderID,))
                result = cursor.fetchone()

                if result[0] is not None:
                    # The order has already been fulfilled, return an error message
                    return (None, "Order already fulfilled")

                # Find the restaurantID of the order
                sql = "SELECT restaurantID FROM FoodOrder WHERE foodOrderID = %s;"
                cursor.execute(sql, (foodOrderID,))
                restaurantID = cursor.fetchone()[0]

                # Retrieve past order data from database
                data = getPastData(connection, cursor, restaurantID)

                # If there is not enough data to make a prediction, return an error message
                if len(data) < 10:
                    return (None, "Sorry, not enough past data exists to make prediction")

                # Split the data into x and y values
                x = np.array([row[0] for row in data]).reshape((-1, 1))
                y = np.array([row[1] for row in data])

                # Create a linear regression model and fit it to the data
                model = LinearRegression().fit(x, y)

                # Retrieve the number of items in the order
                sql = "SELECT COUNT(*) FROM OrderItem WHERE foodOrderID = %s;"
                cursor.execute(sql, (foodOrderID,))
                numItems = cursor.fetchone()[0]

                # Use the model to predict the time taken to fulfill the order
                eta = model.predict(np.array([numItems]).reshape((-1, 1)))[0]

                # Calculate the time elapsed since the order was placed
                sql = "SELECT timeOrdered FROM FoodOrder WHERE foodOrderID = %s;"
                cursor.execute(sql, (foodOrderID,))
                timeOrdered = cursor.fetchone()[0]
                timeElapsed = datetime.now() - timeOrdered

                # Subtract the time elapsed from the predicted time taken to fulfill the order
                eta -= timeElapsed.seconds / 60

                # Return the predicted time taken to fulfill the order
                return (eta, None)

    else:
        # An error has occurred, return the error message
        return (None, connection[1])

# This function retrieves past orders and calculates the time taken to fulfill each order, and the number of items
def getPastData(connection, cursor, restaurantID):
    # Retrieve the timeOrdered, timeFulfilled and foodOrderID for each of the past 100 FoodOrders for the restaurant
    sql = "SELECT timeOrdered, timeFulfilled, foodOrderID FROM FoodOrder WHERE restaurantID = %s AND timeFulfilled IS NOT NULL LIMIT 100;"
    cursor.execute(sql, (restaurantID,))
    result = cursor.fetchall()

    # Iterate through each order and calculate the time taken to fulfill the order
    data = []
    for row in result:
        timeOrdered = row[0]
        timeFulfilled = row[1]
        foodOrderID = row[2]

        # Retrieve the number of items in the order
        sql = "SELECT COUNT(*) FROM OrderItem WHERE foodOrderID = %s;"
        cursor.execute(sql, (foodOrderID,))
        numItems = cursor.fetchone()[0]

        # Calculate the time taken to fulfill the order
        timeTaken = timeFulfilled - timeOrdered

        # Convert the time taken to fulfill the order to an integer number of minutes
        timeTaken = timeTaken.seconds // 60

        # Store the data in a list
        data.append((numItems, timeTaken))

    # Return the data
    return data