from services.db_connection import connect

# This function retrieves all orders which are not yet marked as paid
def retrieveBill(tableID):
    # Attempt to connect to the database
    connection = connect()

    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve the bill for the given tableID
                sql = """
                SELECT
                    FoodOrder.foodOrderID,
                    FoodOrder.price,
                    FoodOrder.timeOrdered,
                    GROUP_CONCAT(CONCAT(MenuItem.name, ' - ', MenuItem.price) SEPARATOR ', ') AS menuItems
                FROM
                    FoodOrder
                INNER JOIN
                    OrderItem ON FoodOrder.foodOrderID = OrderItem.foodOrderID
                INNER JOIN
                    MenuItem ON MenuItem.menuItemID = OrderItem.menuItemID
                WHERE
                    FoodOrder.tableID = %s
                    AND NOT FoodOrder.paid
                GROUP BY
                    FoodOrder.foodOrderID
                ORDER BY FoodOrder.timeOrdered DESC;
                """
                cursor.execute(sql, (tableID,))
                result = cursor.fetchall()

                # Format the result into a list of dictionaries using list comprehension
                orders = [{
                    "foodOrderID": order[0],
                    "price": order[1],
                    "timeOrdered": order[2],
                    "menuItems": order[3]
                } for order in result]

                return (orders, None)
    else:
        # An error occurred connecting to the database, return it
        return (None, connection[1])