from services.db_connection import connect
from email_validator import validate_email, EmailNotValidError

# This class is used for organising data about users of the system
class User:
    def __init__(self, email, name=None):
        # Check if the provided email is valid and deliverable, otherwise return an error
        try:
            email_info = validate_email(email, check_deliverability=True)
            self.email = email_info.email.lower()
        except EmailNotValidError as e:
            # The provided email is invalid, this returns a detailed explanation why
            self.error = str(e)
            return
        
        self.name = name
        
        # Establish whether an account with the provided email already exists
        connection = connect()
        self.error = None
        
        if connection[0] is not None:
            with connection[0] as connection:
                with connection.cursor() as cursor:
                    # Check if a user with the provided email exists already
                    userDetails = self.getUserDetails(cursor, self.email)
                    if userDetails is not None:
                        # User already exists, store their details from the SQL query result
                        self.userID, self.name, self.professional, self.loginAttempts, self.verified = tuple([userDetails[i] for i in range(5)])
                    else:
                        # No user exists, create a new unverified non-professional user
                        if not self.createUser(connection, cursor, self.name, self.email):
                            # An error has occurred, halt execution
                            return
        else:
            # An error has occurred, store it and halt execution
            self.error = connection[1]
            return
    
    def getUserDetails(self, cursor, email):
        # Prepare SQL to be executed
        sql = "SELECT userID, name, professional, loginAttempts, verified FROM User WHERE email = %s;"
        
        # Execute the SQL command
        cursor.execute(sql, (email,))
        result = cursor.fetchone() # None if there are no users
        
        return result
    
    def createUser(self, connection, cursor, name, email):
        # Returns True if success, False if error occurs
        if name is not None:
            sql = """
            INSERT INTO User (name, email, professional, loginAttempts, verified)
            VALUES (%s, %s, 0, 0, 0);
            """
            try:
                cursor.execute(sql, (name, email,))
                connection.commit()
                self.userID = cursor.lastrowid # retrieves primary key for the newly inserted record
            except Exception as e:
                self.error = f"Error occurred during insertion: {e}"
                connection.rollback() # revert changes
                return False
            self.professional, self.loginAttempts, self.verified = 0, 0, 0
            return True
        else:
            # Store an error message and halt execution
            self.error = "An error occurred when creating a new account: Missing parameter \"name\""
            return False