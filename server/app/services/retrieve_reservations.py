from services.db_connection import connect

# This function allows all of a restaurant's reservations to be retrieved
def retrieveReservations(restaurantID):
    # Attempt to connect to the database
    connection = connect()
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve all the restaurant's reservations
                sql = """
                SELECT Reservation.reservationID, Reservation.userID, Reservation.datetime, Reservation.persons,
                Reservation.tableID, User.name, User.email
                FROM Reservation INNER JOIN User ON Reservation.userID = User.userID
                WHERE Reservation.restaurantID = %s;
                """
                cursor.execute(sql, (restaurantID,))
                result = cursor.fetchall()

                # Convert each retrieved reservation into a dictionary
                reservations = []
                for reservation in result:
                    reservationID, userID, reservationDatetime, reservationPersons, tableID, userName, userEmail = reservation
                    reservations.append({
                        "reservationID": reservationID,
                        "userID": userID,
                        "datetime": reservationDatetime,
                        "persons": reservationPersons,
                        "tableID": tableID,
                        "userName": userName,
                        "userEmail": userEmail
                    })

                # Return the retrieved reservations with no error
                return (reservations, None)
    else:
        # An error occurred connecting to the database
        return (None, connection[1])