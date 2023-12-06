from services.db_connection import connect
from services.email import sendEmail

# This class is used for organising data about each table in a restaurant
class Table:
    def __init__(self, restaurantID, tableID=None, capacity=None, tableNumber=None):
        self.__restaurantID = restaurantID
        self.__tableID = tableID
        self.__capacity = capacity
        self.__tableNumber = tableNumber
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

        # If needed, establish whether a table with the provided ID already exists
        if self.__tableID is not None:
            tableExists = self.__checkTableExists()
            if not tableExists[0]:
                # The table does not exist, or an error occurred
                if tableExists[1] is not None:
                    # No error occurred, so create a new table
                    # Check that the required parameters have been provided
                    if self.__capacity is None or self.__tableNumber is None:
                        self.error = "Not all required parameters have been provided"
                        return
                else:
                    # An error did occur
                    self.error = tableExists[1]
                    return
            else:
                # The table does exist, so retrieve information about it
                self.__retrieveData()
        else:
            # No tableID was provided, so create a new table
            if not self.__createNew():
                # An error occurred creating the table, it is stored in self.error
                return

    def __retrieveData(self):
        # This function retrieves data about the table from the database
        sql = "SELECT tableNumber, capacity FROM RestaurantTable WHERE restaurantID = %s AND tableID = %s;"
        self.__cursor.execute(sql, (self.__restaurantID, self.__tableID))
        result = self.__cursor.fetchone()
        self.__tableNumber, self.__capacity = result

    def __checkTableExists(self):
        # This function checks whether a given tableID and restaurantID combination exists in the database
        connection = connect()
        if connection[0] is not None:
            with connection[0] as connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM RestaurantTable WHERE restaurantID = %s AND tableID = %s;"
                    cursor.execute(sql, (self.__restaurantID, self.__tableID))
                    result = cursor.fetchall()
                    # Return True if the table exists, False otherwise
                    return (len(result) != 0, None)
        else:
            # Connection failed, return an error
            return (False, connection[1])

    def __createNew(self):
        # This function creates a new RestaurantTable in the database
        # Check that no table exists with the given table number
        sql = "SELECT * FROM RestaurantTable WHERE restaurantID = %s AND tableNumber = %s;"
        self.__cursor.execute(sql, (self.__restaurantID, self.__tableNumber))
        result = self.__cursor.fetchall()
        if len(result) != 0:
            # A table already exists with the given table number
            self.error = "A table already exists with the given table number"
            return False

        sql = "INSERT INTO RestaurantTable (restaurantID, tableID, tableNumber, capacity) VALUES (%s, %s, %s, %s);"
        try:
            self.__cursor.execute(sql, (self.__restaurantID, self.__tableID, self.__tableNumber, self.__capacity))
            self.__connection.commit()
            return True
        except Exception as e:
            # An error occurred inserting the table
            self.__connection.rollback()
            self.error = f"An error occurred inserting the table: {e}"
            return False

    def editTable(self, tableNumber, capacity):
        # This function allows a table's details to be edited
        # Check that the table number is not already in use
        sql = "SELECT * FROM RestaurantTable WHERE restaurantID = %s AND tableNumber = %s;"
        self.__cursor.execute(sql, (self.__restaurantID, tableNumber))
        result = self.__cursor.fetchall()
        if len(result) != 0:
            # A table already exists with the given table number
            if self.__tableNumber != tableNumber:
                self.error = "A table already exists with the given table number"
                # The table number has been changed, so the table number is already in use
                return False

        # Update the table's details
        sql = "UPDATE RestaurantTable SET tableNumber = %s, capacity = %s WHERE restaurantID = %s AND tableID = %s;"
        try:
            self.__cursor.execute(sql, (tableNumber, capacity, self.__restaurantID, self.__tableID))
            self.__connection.commit()

            # Update the details stored in the object
            self.__tableNumber = tableNumber
            self.__capacity = capacity

            # Delete any future reservations which exceed the table's capacity
            self.__cancelInvalidReservations()

            # Return True to indicate success
            return True
        except Exception as e:
            # An error occurred updating the table
            self.__connection.rollback()
            self.error = f"An error occurred updating the table: {e}"
            return False

    def __cancelInvalidReservations(self):
        # Retrieve all reservations which exceed capacity
        sql = """
        SELECT Reservation.reservationID, Reservation.datetime, User.email
        FROM Reservation INNER JOIN User ON Reservation.userID = User.userID
        WHERE Reservation.restaurantID = %s AND Reservation.tableID = %s
        AND Reservation.persons > %s AND Reservation.datetime > NOW();
        """

        self.__cursor.execute(sql, (self.__restaurantID, self.__tableID, self.__capacity))
        result = self.__cursor.fetchall()

        # Iterate through each invalid reservation
        for reservation in result:
            reservationID, reservationDatetime, userEmail = reservation
            # Delete the reservation
            sql = "DELETE FROM Reservation WHERE reservationID = %s;"
            try:
                self.__cursor.execute(sql, (reservationID,))
                self.__connection.commit()
            except Exception as e:
                # An error occurred deleting the reservation
                self.__connection.rollback()
                self.error = f"An error occurred deleting a future invalid reservation: {e}"
                return

            # Send cancellation email
            sendEmail(userEmail, "Reservation Cancelled", """
            Unfortunately, your reservation at <strong>%s</strong> has been cancelled,
            as the table you reserved is no longer available. We apologise for any inconvenience caused.
            """ % (reservationDatetime))

    def __del__(self):
        # This destructor closes the database connection
        self.__connection.close()