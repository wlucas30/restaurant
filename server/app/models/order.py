from services.db_connection import connect

# This class will be used to represent each food order placed by users
class Order:
    def __init__(self, foodOrderID=None, userID=None, restaurantID=None, tableID=None):
        self.__foodOrderID = foodOrderID
        self.__userID = userID

        # Optional parameters for creating a new order
        self.__restaurantID = restaurantID
        self.__tableID = tableID

        # Any errors that occur are stored here
        self.error = None

        # Establish a database connection
        connection = connect()
        if connection[0] is not None:
            connection = connection[0]
            cursor = connection.cursor()
            self.__connection = connection
            self.__cursor = cursor
        else:
            # An error occurred, store it and halt execution
            self.error = connection[1]
            return

        # If no orderID is provided then a new FoodOrder will be placed
        if self.__foodOrderID is None:
            if not self.__createNew():
                # An error occurred and will be stored in self.error
                return
        else:
            # An orderID has been provided, so attempt to retrieve data about the order
            if not self.__retrieveData():
                # An error occurred and will be stored in self.error
                return

    def __createNew(self):
        # This function creates a new order in the database
        sql = """
        INSERT INTO FoodOrder (userID, restaurantID, tableID, price, timeOrdered, timeFulfilled, confirmed, paid)
        VALUES (%s, %s, %s, 0.00, NOW(), NULL, FALSE, FALSE);
        """

        # Attempt to execute the SQL query
        try:
            self.__cursor.execute(sql, (self.__userID, self.__restaurantID, self.__tableID))
            self.__connection.commit()

            # The order was created successfully, so retrieve the new orderID
            self.__foodOrderID = self.__cursor.lastrowid

            # Store the new database values in the object
            self.__retrieveData()
        except Exception as e:
            self.__connection.rollback()
            self.error = "An error occurred creating the order"
            return False

        return True

    def __retrieveData(self):
        # This function retrieves data about an existing order from the database
        sql = """
        SELECT userID, restaurantID, tableID, price, timeOrdered, timeFulfilled, confirmed, paid
        FROM FoodOrder
        WHERE foodOrderID = %s;
        """
        self.__cursor.execute(sql, (self.__foodOrderID,))
        result = self.__cursor.fetchone()

        # Check that the order exists
        if result is None:
            self.error = "The order does not exist"
            return False
        else:
            # The order exists, so store the data
            self.__userID, self.__restaurantID, self.__tableID, self.__price, self.__timeOrdered, self.__timeFulfilled, self.__confirmed, self.__paid = result
            return True

    def addItem(self, menuItemID, quantity=1):
        # This function adds an item to the order
        # Check that the menuItemID exists and is associated with the restaurant
        sql = """
        SELECT menuItemID
        FROM MenuItem
        WHERE restaurantID = %s AND menuItemID = %s;
        """
        self.__cursor.execute(sql, (self.__restaurantID, menuItemID))
        result = self.__cursor.fetchone()
        if result is None:
            self.error = "The menu item does not exist"
            return False

        for _ in range(quantity):
            # Repeat this process for each item to be added
            sql = """
            INSERT INTO OrderItem (foodOrderID, menuItemID)
            VALUES (%s, %s);
            """
            try:
                self.__cursor.execute(sql, (self.__foodOrderID, menuItemID))
                self.__connection.commit()
            except Exception as e:
                self.__connection.rollback()
                self.error = "An error occurred adding the item to the order"
                return False

            # Update the price of the order
            sql = """
            UPDATE FoodOrder
            SET price = price + (SELECT price FROM MenuItem WHERE menuItemID = %s)
            WHERE foodOrderID = %s;
            """
            try:
                self.__cursor.execute(sql, (menuItemID, self.__foodOrderID))
                self.__connection.commit()
            except Exception as e:
                self.__connection.rollback()
                self.error = "An error occurred updating the order price"
                return False

            # Update the price of the order object
            sql = "SELECT price FROM FoodOrder WHERE foodOrderID = %s;"
            self.__cursor.execute(sql, (self.__foodOrderID,))
            self.__price = self.__cursor.fetchone()[0]

            # The item was added successfully
            continue
        return True

    def orderStatus(self, confirmed=False, fulfilled=False, paid=False):
        # This function allows an order to be confirmed or rejected, or marked as fulfilled, or marked as paid
        if fulfilled:
            # Mark the order as fulfilled
            sql = """
            UPDATE FoodOrder
            SET timeFulfilled = NOW(), confirmed = TRUE
            WHERE foodOrderID = %s;
            """
        elif paid:
            # Mark the order as paid
            sql = """
            UPDATE FoodOrder
            SET paid = TRUE, confirmed = TRUE
            WHERE foodOrderID = %s;
            """
        elif confirmed:
            # Mark the order as confirmed
            sql = """
            UPDATE FoodOrder
            SET confirmed = TRUE
            WHERE foodOrderID = %s;
            """
        elif not confirmed and not (fulfilled or paid):
            # This is a request to reject the order, so delete the order
            sql = """
            DELETE FROM FoodOrder
            WHERE foodOrderID = %s;
            """

        # Attempt to execute the SQL query
        try:
            self.__cursor.execute(sql, (self.__foodOrderID,))
            self.__connection.commit()
            return True
        except Exception as e:
            self.__connection.rollback()
            self.error = "An error occurred updating the order status"
            return False

    def getFoodOrderID(self):
        return self.__foodOrderID

    def getRestaurantID(self):
        return self.__restaurantID

    def __del__(self):
        # Close the database connection when the object is destroyed
        self.__connection.close()