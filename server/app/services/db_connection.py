from dotenv import load_dotenv
import os
import mysql.connector

# This function retrieves the database password securely from the environment
def getDbPassword():
    # Initialise the environment variables
    load_dotenv()
    
    password, error = None, None
    try:
        password = os.getenv("DB_PASSWORD")
    except:
        # An error has occurred retrieving the password
        error = "An error occurred retrieving the database credentials"
    
    return password, error

# This function attempts to create a connection with the database
def connect():
    # Initialise connection and error to be returned
    connection, error = None, None
    
    # Attempt to retrieve database credentials
    password = getDbPassword()
    
    # Check if any errors occurred
    if password[0] != None:
        # Remove blank error message from password
        password = password[0]
        
        # Connection is nested in a try statement to catch any errors during connection
        try:
            connection = mysql.connector.connect(
                host = "localhost",
                user = "tablenest",
                passwd = password,
                database = "restaurant"
            )
        except mysql.connector.Error as e:
            # Error message is substituted into the string
            error = f"Database connection failed: {e}"
        
        # Returns a tuple containing the connection object or any error
        return connection, error
    else:
        # Return error message
        return None, password[1]
