import numpy as np
import random
from services.db_connection import connect
from matplotlib import pyplot as plt

# This function inserts 50 random past orders into the database for testing purposes
def testData(restaurantID):
    connection = connect()
    
    with connection[0] as connection:
        with connection.cursor() as cursor:
            x = [] # number of items
            y = [] # time taken
            for i in range(50):
                # Generate a random number of items in the order
                numItems = np.random.randint(1, 10)
                x.append(numItems)

                # Generate a random time taken to fulfill the order which correlates with the number of items
                timeTaken = random.uniform(3,5) * numItems
                y.append(timeTaken)

                # Generate a random timeOrdered
                timeOrdered = np.random.randint(0, 1000000000)

                # Generate the timeFulfilled
                timeFulfilled = timeOrdered + (timeTaken * 60)

                # Insert the order into the database
                sql = "INSERT INTO FoodOrder (restaurantID, timeOrdered, timeFulfilled, userID, tableID, price, confirmed, paid) VALUES (%s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), 0, 0, 0, 0, 0);"
                cursor.execute(sql, (restaurantID, timeOrdered, timeFulfilled))

                # Retrieve the foodOrderID of the last inserted order
                sql = "SELECT LAST_INSERT_ID();"
                cursor.execute(sql)
                foodOrderID = cursor.fetchone()[0]

                # Insert the items into the database
                for j in range(numItems):
                    sql = "INSERT INTO OrderItem (foodOrderID, menuItemID) VALUES (%s, 0);"
                    cursor.execute(sql, (foodOrderID,))

            # Commit the changes to the database
            connection.commit()
            
            # Show generated data on a scatter graph
            plt.scatter(x, y)
            plt.title("Test data correlation")
            plt.xlabel("Number of items")
            plt.ylabel("Waiting time in minutes")
            plt.show()