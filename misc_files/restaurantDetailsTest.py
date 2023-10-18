# sql test

import mysql.connector
from mysql.connector import Error
from json import dumps

def connect_db():
    # Initialise connection
    connection = None
    
    # Catch any errors connecting to database
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="tablenest",
            passwd="gGLm]baH-u(Q)m0(",
            database="restaurant"
        )
    except Error as e:
        print("Database connection failed:", e)
    
    return connection

def details(restaurantID):
    with connect_db() as connection:
        with connection.cursor() as cursor:
            sql = """
                    SELECT
                    	Restaurant.name,
                    	Restaurant.description,
                    	Restaurant.category,
                    	Restaurant.location,
                    	GROUP_CONCAT(CONCAT(OpeningPeriod.dayOfWeek, ': ', OpeningPeriod.openingTime, ' - ', OpeningPeriod.closingTime) ORDER BY OpeningPeriod.dayOfWeek ASC SEPARATOR ', ') AS openingPeriods
                    FROM
                    	Restaurant
                    INNER JOIN
                    	OpeningPeriod ON Restaurant.restaurantID = OpeningPeriod.restaurantID
                    WHERE
                    	Restaurant.restaurantID = %s;
                  """
            # extra comma is needed to express the 2nd parameter as a tuple
            cursor.execute(sql, (restaurantID,))
            
            column_names = [description[0] for description in cursor.description]
            result = cursor.fetchone()
            if result:
                result_dict = dict(zip(column_names, result))
            else:
                print("Failed to convert restaurant details")
            
            cursor.close()
            
            result_dict["openingPeriods"] = openingPeriodsDict(result_dict["openingPeriods"])
            
            return dumps(result_dict)
            
        connection.close()
        
def openingPeriodsDict(opening_periods):
    periods_array = opening_periods.split(", ")
    results = {}
    
    for period in periods_array:
        day_of_week = period[0]
        open_time = period[3:8]
        close_time = period[14:19]
        results[day_of_week] = {"open" : open_time, "close" : close_time}
    
    return results