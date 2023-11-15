from services.db_connection import connect

# This function returns all of the stored reviews for a given restaurantID
def getReviews(restaurantID):
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve reviews
                sql = """
                SELECT
                    User.name, Review.rating, Review.title, Review.body
                FROM 
                    Review INNER JOIN User
                ON Review.userID = User.userID
                WHERE Review.restaurantID = %s;
                """
                cursor.execute(sql, (restaurantID,))
                result = cursor.fetchall()
                
                # Store each retrieved review as a dictionary
                reviews = []
                for row in result:
                    review = {
                        "username": row[0],
                        "rating": row[1],
                        "title": row[2],
                        "body": row[3]
                    }
                    reviews.append(review)
                
                # Return without any errors
                return (reviews, None)
    else:
        # An error has occurred, return the error message
        return (False, connection[1])