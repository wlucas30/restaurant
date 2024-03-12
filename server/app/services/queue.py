from services.db_connection import connect

# This function retrieves unfulfilled orders after a provided foodOrderID
def getUnfulfilledOrders(restaurantID, foodOrderID=0): # default value of 0 will return all unfulfilled orders
    # Establish a database connection
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            cursor = connection.cursor()
            # Retrieve unfulfilled orders after the provided foodOrderID
            sql = """
            SELECT foodOrderID, userID, restaurantID, tableID, price, timeOrdered, confirmed, customisation
            FROM FoodOrder
            WHERE restaurantID = %s AND foodOrderID > %s AND timeFulfilled IS NULL;
            """
            cursor.execute(sql, (restaurantID, foodOrderID))
            result = cursor.fetchall()

            # Format the result into a list of dictionaries using list comprehension
            result = [{
                "foodOrderID": order[0],
                "userID": order[1],
                "restaurantID": order[2],
                "tableID": order[3],
                "price": order[4],
                "timeOrdered": order[5],
                "confirmed": order[6] == 1, # converts 0/1 to False/True
                "customisation": order[7]
            } for order in result]

            # Retrieve all of the OrderItems for each order
            for order in result:
                sql = """
                SELECT MenuItem.name, MenuItem.section, MenuItem.price
                FROM OrderItem INNER JOIN MenuItem
                ON OrderItem.menuItemID = MenuItem.menuItemID
                WHERE OrderItem.foodOrderID = %s;
                """
                cursor.execute(sql, (order["foodOrderID"],))

                # Append the order items to the order dictionary using list comprehension
                order["orderItems"] = [{
                    "name": item[0],
                    "section": item[1],
                    "price": item[2]
                } for item in cursor.fetchall()]

            return (result, None)
    else:
        # An error occurred connecting to the database, return it
        return (None, connection[1])