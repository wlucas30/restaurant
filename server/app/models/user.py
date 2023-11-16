from services.db_connection import connect
from email_validator import validate_email, EmailNotValidError
from services.authenticate import authenticate

# This class is used for organising data about users of the system
class User:
    def __init__(self, email=None, name=None, userID=None):
        self.error = None
        
        if email is not None:
            # Check if the provided email is valid and deliverable, otherwise return an error
            try:
                email_info = validate_email(email, check_deliverability=True)
                self.email = email_info.email.lower()
                self.userID = None
            except EmailNotValidError as e:
                # The provided email is invalid, this returns a detailed explanation why
                self.error = str(e)
                return
        else:
            self.userID = userID
            self.email = None
            
        self.name = name
        
        # Establish whether an account with the provided email already exists
        connection = connect()
        if connection[0] is not None:
            with connection[0] as connection:
                with connection.cursor() as cursor:
                    # Check if a user with the provided email exists already
                    userDetails = self.getUserDetails(cursor, self.email, self.userID)
                    if userDetails is not None:
                        # User already exists, store their details from the SQL query result
                        self.email, self.userID, self.name, self.professional, self.loginAttempts, self.verified = tuple([userDetails[i] for i in range(6)])
                    else:
                        # No user exists, create a new unverified non-professional user
                        if not self.createUser(connection, cursor, self.name, self.email):
                            # An error has occurred, halt execution
                            return
        else:
            # An error has occurred, store it and halt execution
            self.error = connection[1]
            return
    
    def getUserDetails(self, cursor, email=None, userID=None):
        # Prepare SQL to be executed
        if email is not None:
            sql = "SELECT email, userID, name, professional, loginAttempts, verified FROM User WHERE email = %s;"
            
            # Execute the SQL command
            cursor.execute(sql, (email,))
        else:
            sql = "SELECT email, userID, name, professional, loginAttempts, verified FROM User WHERE userID = %s;"
            
            # Execute the SQL command
            cursor.execute(sql, (userID,))
            
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
    
    def changeEmail(self, new_email, auth_token):
        # Check that the provided authentication token is valid
        authentication = authenticate(self.userID, auth_token)
        
        if not authentication[0]:
            self.error = authentication[1]
            return
        
        connection = connect()
        if connection[0] is not None:
            with connection[0] as connection:
                with connection.cursor() as cursor:
                    # Change the stored email in the database
                    sql = "UPDATE User SET email = %s, verified=0 WHERE userID = %s;"
                    # Delete any stored authentication tokens or verification codes
                    sql2 = "DELETE FROM AuthenticationToken WHERE userID = %s";
                    sql3 = "DELETE FROM VerificationCode WHERE userID = %s;"
                    try:
                        cursor.execute(sql, (new_email, self.userID))
                        cursor.execute(sql2, (self.userID,))
                        cursor.execute(sql3, (self.userID,))
                        connection.commit()
                    except Exception as e:
                        self.error = f"Error occurred during database operation: {e}"
                        connection.rollback() # revert changes
                        return
                    
                    self.email = new_email
                    return
        else:
            # An error has occurred, store it and halt execution
            self.error = connection[1]
            return

# This class inherits from the User class
class ProfessionalUser(User):
    def __init__(self, userID):
        super().__init__(userID=userID)
        
        if self.error is not None:
            return
        
        # Promote to professional if necessary
        if not bool(self.professional):
            self.promoteToProfessional()
            if self.error is not None:
                return
        
    def getRestaurant():
        return
    
    def promoteToProfessional():
        # Change user professional attribute to 1
        # Create blank restaurant ({name}'s restaurant)
        return