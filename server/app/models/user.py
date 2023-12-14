from services.db_connection import connect
from email_validator import validate_email, EmailNotValidError

# This class is used for organising data about users of the system
class User:
    def __init__(self, email=None, name=None, userID=None):
        self.error = None
        
        if email is not None:
            self.userID = None
            if not self.validateEmail(email):
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
        from services.authenticate import authenticate
        # Validate the provided email
        if not self.validateEmail(new_email):
            return
        
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
                    sql2 = "DELETE FROM AuthToken WHERE userID = %s";
                    sql3 = "DELETE FROM VerificationCode WHERE userID = %s;"
                    try:
                        cursor.execute(sql, (self.email, self.userID))
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
    
    def validateEmail(self, email):
        # Check if the provided email is valid and deliverable, otherwise return an error
        try:
            email_info = validate_email(email, check_deliverability=True)
            self.email = email_info.email.lower()
            return True
        except EmailNotValidError as e:
            # The provided email is invalid, this returns a detailed explanation why
            self.error = str(e)
            return False

# This class inherits from the User class
class ProfessionalUser(User):
    def __init__(self, userID):
        # Initialise a User object with the given userID
        super().__init__(userID=userID)
        
        if self.error is not None:
            # An error has occurred and is stored in self.error, halt execution
            return
        
        # Attempt to connect to the database
        connection = connect()
        if connection[0] is not None:
            with connection[0] as connection:
                with connection.cursor() as cursor:
                    # Check if the user is a professional, if not then promote them
                    if not bool(self.professional):
                        # Change the user to a professional
                        self.promoteToProfessional(connection, cursor)
                        # Check for errors
                        if self.error is not None:
                            return
                        
                        # Create a new blank restaurant
                        self.createRestaurant(connection, cursor)
                        return
                    
                    # Retrieve the restaurantID of this ProfessionalUser's restaurant
                    self.restaurantID = self.getRestaurantID(cursor)
        else:
            # An error has occurred, store it and halt execution
            self.error = connection[1]
            return
    
    def promoteToProfessional(self, connection, cursor):
        # Change user professional attribute to 1
        sql = "UPDATE User SET professional = 1 WHERE userID = %s;"
        try:
            cursor.execute(sql, (self.userID,))
            connection.commit()
            self.professional = 1
        except Exception as e:
            # An error occurred updating the User
            self.error = str(e)
            connection.rollback()
            return
    
    def createRestaurant(self, connection, cursor):
        # Create a new blank restaurant managed by this ProfessionalUser
        sql = """
        INSERT INTO Restaurant (managerUserID, name, description, category, location)
        VALUES (%s, "New Restaurant", "No details yet...", "None", "0, 0");
        """
        try:
            cursor.execute(sql, (self.userID,))
            connection.commit()
        except Exception as e:
            # An error has occurred creating a restaurant
            self.error = str(e)
            connection.rollback()
            return
        
    def getRestaurantID(self, cursor):
        # Retrieve the restaurantID stored for this user's restaurant
        sql = "SELECT restaurantID FROM Restaurant WHERE managerUserID = %s;"
        cursor.execute(sql, (self.userID,))
        return cursor.fetchone()[0]