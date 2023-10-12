testdata = [
    # (ID, distance from user in miles)
    (1, 10),
    (2, 0.5),
    (3, 9),
    (4, 3),
    (5, 15),
    (6, 7.5),
    (7, 2),
    (8, 11),
    (9, 6),
    (10, 8),
    (11, 1),
    (12, 12.5),
    (13, 4),
    (14, 14),
    (15, 5),
    (16, 2.5),
    (17, 13),
    (18, 6.5),
    (19, 9.5),
    (20, 0.2)
]

def sortRestaurants(restaurants):
    if len(restaurants) > 1:
        midpoint = len(restaurants) // 2
        left = sortRestaurants(restaurants[:midpoint])
        right = sortRestaurants(restaurants[midpoint:])
        
        merged = mergeRestaurants(left, right)
        
        return merged
    else:
        return restaurants
    
def mergeRestaurants(left, right):
    print(left, right)
    sortedRestaurants = []
    
    leftPointer, rightPointer = 0, 0
    
    while leftPointer < len(left) and rightPointer < len(right):
        if left[leftPointer][1] <= right[rightPointer][1]:
            sortedRestaurants.append(left[leftPointer])
            leftPointer += 1
        else:
            sortedRestaurants.append(right[rightPointer])
            rightPointer += 1
    
    while leftPointer < len(left):
        sortedRestaurants.append(left[leftPointer])
        leftPointer += 1
    
    while rightPointer < len(right):
        sortedRestaurants.append(right[rightPointer])
        rightPointer += 1
    
    return sortedRestaurants