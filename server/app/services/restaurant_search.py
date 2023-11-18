from services.db_connection import connect

def restaurantSearch(search_term):
    # Retrieve all restaurant names and IDs
    restaurantNames = getRestaurantNames()
    if restaurantNames[0] == None:
        # An error has occurred
        return (None, restaurantNames[1])
    else:
        restaurantNames = restaurantNames[0]
    
    # Calculate and store the Levenshtein distance for each restaurant
    for i in range(len(restaurantNames)):
        restaurant = restaurantNames[i]
        name = restaurant[1]
        
        # If the restaurant name is longer than the search term then only compare the
        # first part of the restaurant name so that the lengths are equal
        if len(name) > len(search_term):
            name = name[:len(search_term)]
            
        distance = calculateLevenshteinDistance(name, search_term)
        
        # Store the distance in the tuple
        # (restaurantID, name, levenshteinDistance)
        restaurantNames[i] = (restaurant[0], restaurant[1], distance)
        
    # Return the ordered list of restaurants
    return (orderByDistance(restaurantNames), False)
    
def getRestaurantNames():
    # This function returns every stored restaurant name, matched to a restaurantID
    # Attempt to connect to the database
    connection = connect()
    
    if connection[0] is not None:
        with connection[0] as connection:
            with connection.cursor() as cursor:
                sql = "SELECT restaurantID, name FROM Restaurant;"
                cursor.execute(sql)
                result = cursor.fetchall()
                
                # This list comprehension creates an array in the format:
                # [(restaurantID, name)]
                restaurantNames = [(row[0], row[1]) for row in result]
                return (restaurantNames, None)
    else:
        # An error has occurred, return the error message
        return (None, connection[1])

# Merge sort algorithm
def orderByDistance(restaurantNames):
    # Format of restaurantNames: [(restaurantID, name, levenshteinDistance)]
    if len(restaurantNames) == 1:
        return restaurantNames # base case
    # Split into two halves recursively
    midpoint = len(restaurantNames) // 2
    left = orderByDistance(restaurantNames[:midpoint])
    right = orderByDistance(restaurantNames[midpoint:])
    
    # Merge the halves together into a sorted array
    return mergeRestaurants(left, right)

# This merges two lists of sorted restaurants
def mergeRestaurants(left, right):
    sortedRestaurants = [] # prepare empty array for sorting
    leftPointer, rightPointer, numSorted = 0, 0, 0
    
    # Continously add the smallest distance restaurant from each half
    while leftPointer < len(left) and rightPointer < len(right) and numSorted < 10:
        if left[leftPointer][2] < right[rightPointer][2]:
            sortedRestaurants.append(left[leftPointer])
            leftPointer += 1
            numSorted += 1
        else:
            sortedRestaurants.append(right[rightPointer])
            rightPointer += 1
            numSorted += 1
    
    # Add any remaining restaurants
    while leftPointer < len(left) and numSorted < 10:
        sortedRestaurants.append(left[leftPointer])
        leftPointer += 1
        numSorted += 1
    while rightPointer < len(right) and numSorted < 10:
        sortedRestaurants.append(right[rightPointer])
        rightPointer += 1
        numSorted += 1

    return sortedRestaurants

def calculateLevenshteinDistance(term1, term2):
    # Convert both arguments to lowercase for case-insensitive comparison
    term1 = term1.lower()
    term2 = term2.lower()
    
    # Ensure that term1's length is longer than or equal to term2
    if len(term1) < len(term2):
        # If not, swap the terms to make term1 longer or equal in length
        return calculateLevenshteinDistance(term2, term1)
    
    # If one of the terms is empty, the distance is equal to the length of the other
    if len(term2) == 0:
        return len(term1)

    # Initialize the previous row to be the range of the length of term2 plus 1
    previous_row = range(len(term2) + 1)
    
    # Iterate through each character in term1
    for i, char1 in enumerate(term1):
        # Initialize the current row with the first element as the index in term1
        current_row = [i + 1]
        
        # Iterate through each character in term2
        for j, char2 in enumerate(term2):
            # Calculate the cost of insertions, deletions, and substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (char1 != char2)
            
            # Append the minimum cost to the current row
            current_row.append(min(insertions, deletions, substitutions))
        
        # Update the previous row with the current row for the next iteration
        previous_row = current_row
    
    # Return the last element of the previous row, which represents the Levenshtein distance
    return previous_row[-1]