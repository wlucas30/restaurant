#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request
import json
import mysql.connector
from mysql.connector import Error
from geopy import distance

# This sets the app name to the same name as this file
app = Flask(__name__)

# This determines which page must be requested to call main()
@app.route("/nearbyRestaurants", methods=["POST"])
def main():
    # This function should take the input parameters of Latitude and Longitude,
    # then return the 10 nearest restaurants in ascending order of distance
    # by retrieving these from the database.
    
    # Indicates JSON format for the HTTP request response
    print("Content-Type: application/json\n")
    
    # Converts request parameters from JSON to Python format
    data = request.json
    
    # Initialise empty dictionary for restaurants and their distances from the user
    # Key:Value = restaurantID:distance
    distance_dict = {}
    
    # Initialise connection to the database
    connection = connect_db()
    
    with connection:
        with connection.cursor() as cursor:
            # Retrieve all records from Restaurant table
            sql = "SELECT restaurantID, location FROM Restaurant"
            cursor.execute(sql)
            
            # Iterate through each returned restaurant record
            for row in cursor:
                restaurantID, location = row["restaurantID"], row["location"]
                
                # Location is in format (latitude,longitude)
                # Find position of the seperator between latitude and longitude
                seperator_index = location.index(",")
                
                # Seperate location into latitude and longitude
                latitude, longitude = location[1:seperator_index], location[seperator_index+1:-1]
                
                # Calculate distance between user and restaurant
                distance = distance_calc(latitude, longitude, data["latitude"], data["longitude"])
                
                # Add distance to the dictionary
                distance_dict[restaurantID] = distance
        
        # Close connection
        connection.close()
    
    # Order the restaurants by distance in ascending order (returns only closest 10)
    restaurants = order_restaurants(distance_dict)
    
    # Serialise the restaurants array as JSON for returning to the front-end
    restaurants_json = json.dumps(restaurants)
    
    # Output the restaurants to the front-end
    print(restaurants_json)

# This function calculates the distance between two sets of coordinates
def distance_calc(lat1, lon1, lat2, lon2):
    coords_1, coords_2 = (lat1, lon1), (lat2, lon2)
    
    return distance.geodesic(coords_1, coords_2).miles

# Sorts a dictionary of format {restaurantID:distance} in ascending order of distance,
# returning only the closest 10 values
def order_restaurants(distance_dict):
    return "Code here"

# This function attempts to create a connection with the database and returns the connection if successful
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

if __name__ == "__main__":
    app.run(host="localhost", port=8080)