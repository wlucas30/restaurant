from services.db_connection import connect

# This function inserts a given menu item to the database
def addMenuItem(restaurantID, menuSection, name, description, calories, price):
    # Perform data validation
    validation = validate(menuSection, name, description, calories, price)
    if not validation[0]:
        # Validation failed, return the error message
        return (False, validation[1])

    # Attempt to connect to the database
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Insert the menu item into the database
                sql = """
                INSERT INTO MenuItem (restaurantID, section, name, description, calories, price)
                VALUES (%s, %s, %s, %s, %s, %s);
                """
                try:
                    cursor.execute(sql, (restaurantID, menuSection, name, description, calories, price))
                    connection.commit()
                except Exception as e:
                    # An error occurred inserting the menu item
                    return (False, f"An error occurred inserting the menu item: {e}")
    else:
        # An error occurred connecting to the database
        return (False, connection[1])

    # The menu item has been inserted successfully
    return (True, None)

def validate(menuSection, name, description, calories, price):
    # Check that the menuSection is a string
    if type(menuSection) is not str:
        return (False, "The menuSection must be a string")
    # Check the length of menuSection
    if len(menuSection) > 50:
        return (False, "The menuSection must not exceed 50 characters")

    # Check that the name is a string
    if type(name) is not str:
        return (False, "The name must be a string")
    # Check the length of name
    if len(name) > 50:
        return (False, "The name must not exceed 50 characters")

    # Check that the description is a string
    if type(description) is not str:
        return (False, "The description must be a string")

    # Check that the calories is an integer
    if type(calories) is not int:
        return (False, "The calories must be an integer")

    # Check that the price is a float
    if type(price) is not float:
        return (False, "The price must be a float")
    # Check that the price has no more than 2 decimal places
    if len(str(price).split(".")[1]) > 2:
        return (False, "The price must have no more than 2 decimal places")

    # All validation passed, return no error message
    return (True, None)

def deleteMenuItem(menuItemID, restaurantID):
    # Attempt to connect to the database
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Delete the menu item from the database
                sql = "DELETE FROM MenuItem WHERE menuItemID = %s AND restaurantID = %s;"
                # We also need to delete any OrderItems to maintain referential integrity
                sql2 = "DELETE FROM OrderItem WHERE menuItemID = %s;"
                try:
                    cursor.execute(sql, (menuItemID, restaurantID))
                    cursor.execute(sql2, (menuItemID,))
                    connection.commit()
                except Exception as e:
                    # An error occurred deleting the menu item or order items
                    connection.rollback()
                    return (False, f"An error occurred during deletion: {e}")
    else:
        # An error occurred connecting to the database
        return (False, connection[1])

    # The menu item has been deleted successfully
    return (True, None)