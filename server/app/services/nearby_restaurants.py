from geopy.distance import geodesic as gd
from services.db_connection import connect

# This function returns an ordered list of restaurants near the provided location
def getNearbyRestaurants(location):    
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve all restaurantID from database
                sql = "SELECT restaurantID, location FROM Restaurant;"
                cursor.execute(sql)
                result = cursor.fetchall()
                
                # This dictionary is used to store the distance between each restaurant
                # and the provided location
                distances = {}
                
                for row in result:
                    restaurantID = row[0]
                    restaurantLocation = row[1]
                    
                    # Calculate distance in miles from given location to restaurant
                    distance = gd(location, restaurantLocation).miles
                    
                    # Store in dictionary
                    distances[restaurantID] = distance
                    
                # Reformat the dictionary into an array of tuples
                distances = [(restaurantID, distance) for restaurantID, distance in distances.items()]
                
                # Return the sorted restaurantIDs with no error message
                return (sortRestaurants(distances), None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])
    
# This function sorts a given list of restaurantIDs in ascending order of distance
def sortRestaurants(distances):
    # If the provided array is only of length 1 then it is already sorted
    if len(distances) == 1:
        return distances
    
    # Recursively split the provided array and merge the halves together
    midpoint = len(distances) // 2
    left = sortRestaurants(distances[:midpoint])
    right = sortRestaurants(distances[midpoint:])
    
    return mergeRestaurants(left, right)

# This function merges together halves of ordered arrays
def mergeRestaurants(left, right):
    # An empty array is initialised for storing the sorted result
    sortedRestaurants = []
    
    # Two pointers for iterating through each half
    leftPointer, rightPointer = 0, 0
    
    # Only return 10 results at maximum
    while (leftPointer + rightPointer < 10) and (leftPointer < len(left) or rightPointer < len(right)):
        while leftPointer < len(left) and rightPointer < len(right):
            # Compare the distance from both halves
            if left[leftPointer][1] <= right[rightPointer][1]:
                sortedRestaurants.append(left[leftPointer])
                leftPointer += 1
            else:
                sortedRestaurants.append(right[rightPointer])
                rightPointer += 1
        
        # Add any leftover elements to the sorted array
        while leftPointer < len(left):
            sortedRestaurants.append(left[leftPointer])
            leftPointer += 1
        
        while rightPointer < len(right):
            sortedRestaurants.append(right[rightPointer])
            rightPointer += 1

    return sortedRestaurants
    
# This function returns at most 10 random restaurantIDs
def getRandomRestaurants(): 
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                # Retrieve 10 random restaurantIDs from database
                sql = "SELECT restaurantID FROM Restaurant ORDER BY RAND() LIMIT 10;"
                cursor.execute(sql)
                result = cursor.fetchall()
                
                # Store the restaurantIDs in an array
                restaurants = [row[0] for row in result]
                
                # Return this array with no error message
                return (restaurants, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])