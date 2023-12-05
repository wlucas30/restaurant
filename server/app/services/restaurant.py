from services.db_connection import connect

# This function allows all of a restaurant's tables to be retrieved
def getTables(restaurantID):
    # Attempt to connect to the database
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve all of the restaurant's tables
                sql = "SELECT tableID, tableNumber, capacity FROM RestaurantTable WHERE restaurantID = %s;"
                try:
                    cursor.execute(sql, (restaurantID,))
                    result = cursor.fetchall()
                except Exception as e:
                    # An error occurred retrieving the tables
                    return (None, f"An error occurred retrieving the tables: {e}")

                # Convert each retrieved table into a dictionary
                tables = []
                for table in result:
                    tableID, tableNumber, capacity = table
                    tables.append({
                        "tableID": tableID,
                        "tableNumber": tableNumber,
                        "capacity": capacity
                    })

                # Return the retrieved tables with no error
                return (tables, None)
    else:
        # An error occurred connecting to the database
        return (None, connection[1])