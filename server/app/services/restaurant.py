from datetime import datetime
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

def setOpeningPeriods(restaurantID, openingPeriods):
    print("Hello")
    # Ensure that the provided opening periods are valid
    if not validateOpeningPeriods(openingPeriods):
        return (False, "Invalid opening periods provided")

    # Attempt to connect to the database
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                print("Hi")
                # Delete all of the restaurant's existing opening periods
                sql = "DELETE FROM OpeningPeriod WHERE restaurantID = %s;"
                try:
                    cursor.execute(sql, (restaurantID,))
                    connection.commit()
                except Exception as e:
                    # An error occurred deleting the opening periods
                    return (False, f"An error occurred deleting the current opening periods: {e}")

                # Insert the provided opening periods into the database
                sql = """INSERT INTO OpeningPeriod (restaurantID, dayOfWeek, openingTime, closingTime)
                VALUES (%s, %s, %s, %s);"""
                for day, value in openingPeriods.items():
                    openingTime = value["openingTime"]
                    closingTime = value["closingTime"]
                    try:
                        cursor.execute(sql, (restaurantID, int(day), openingTime, closingTime))
                        connection.commit()
                    except Exception as e:
                        # An error occurred inserting the opening period
                        return (False, f"An error occurred inserting the opening period: {e}")

                # Return no error
                return (True, None)
    else:
        # An error occurred connecting to the database
        return (False, connection[1])
def validateOpeningPeriods(openingPeriods):
    # Ensure that the opening periods are provided in the correct format
    if type(openingPeriods) is not dict:
        return False
    if len(openingPeriods) == 0 or len(openingPeriods) > 7:
        return False
    # Ensure that all stored days have an opening and closing tiem stored
    for key, value in openingPeriods.items():
        # Check that the key can be converted to an integer between 1 and 7
        try:
            key = int(key)
            if type(key) != int or key < 1 or key > 7:
                # Day of week is not an integer between 1 and 7
                return False
        except ValueError:
            # Day of week is not an integer
            return False

        try:
            openingTime = value["openingTime"]
            closingTime = value["closingTime"]
        except KeyError:
            # The opening period does not have either an opening or closing time
            return False

        # Attempt to convert the opening and closing times into datetime.time objects
        try:
            openingTime = datetime.strptime(openingTime, "%H:%M").time()
            closingTime = datetime.strptime(closingTime, "%H:%M").time()
        except ValueError:
            # The opening or closing time is not in the correct format
            return False

        # Ensure that the opening time is before the closing time
        if openingTime >= closingTime:
            return False

    return True