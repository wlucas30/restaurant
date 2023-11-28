from flask import Flask, request, jsonify
from services.nearby_restaurants import getNearbyRestaurants, getRandomRestaurants
from services.restaurant_details import getRestaurantDetails
from services.email_verification import beginVerification
from services.check_verification import checkVerificationCode
from services.auth_token import getAuthToken
from services.authenticate import authenticate
from services.make_review import makeReview
from services.get_reviews import getReviews
from services.restaurant_search import restaurantSearch
from services.reservation_availability import getAvailableReservations
from services.make_reservation import makeReservation
from services.update_restaurant import updateRestaurant
from services.save_image import saveRestaurantImage
from services.get_image import getRestaurantImages
from services.delete_image import deleteRestaurantImage
from services.menu_item import addMenuItem, deleteMenuItem, changeMenuItem
from datetime import datetime
from models.user import User, ProfessionalUser
import json

# This sets the app name
app = Flask("tableNest")

@app.route("/nearbyRestaurants", methods=["POST"])
def nearbyRestaurants():
    """
    This function takes an input from the POST request, user location.
    It then calls the nearby_restaurants service which finds the nearest 10 (at most)
    restaurants, which will be returned to the client in JSON format.
    """
    
    # Prepares response to be returned to the client
    response = {
        "restaurants" : None,
        "error" : None
    }
    
    # Attempts to convert POST request parameters from JSON to Python format
    latitude, longitude, random = None, None, False
    try:
        data = request.json
        latitude, longitude, random = data["latitude"], data["longitude"], data["random"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    if not random:
        # Get array of nearby restaurants and their respective distances
        distances = getNearbyRestaurants((latitude, longitude))
        
        if distances[0] is not None:
            # No error has occurred
            response["restaurants"] = distances[0]
            
            return jsonify(response)
        else:
            # An error has occurred, stop execution here and return it to the client
            response["error"] = distances[1]
            
            return jsonify(response)
    else:
        # No location is provided, so return random restaurants
        randomRestaurants = getRandomRestaurants()
        
        # Encode the function output into the response 
        response["restaurants"], response["error"] = randomRestaurants
        
        return jsonify(response)
    
@app.route("/restaurantDetails", methods=["POST"])
def restaurantDetails():
    """
    This function takes an input from the POST request, a restaurantID.
    It then calls the restaurant_details service which retrieves restaurant information
    from the database and returns it.
    """
    
    # Prepares response to be returned to the client
    response = {
        "details" : None,
        "error" : None
    }
    
    # Attempts to convert POST request parameters from JSON to Python format
    restaurantID = None
    try:
        data = request.json
        restaurantID = data["restaurantID"]
    except KeyError:
        response["error"] = "Missing required parameter"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        response["error"] = "An unknown exception occured:", str(e)
        return jsonify(response)
    
    details = getRestaurantDetails(restaurantID)
    
    if details[0] is not None:
        response["details"] = details[0]
        return jsonify(response)
    else:
        # An error has occured
        response["error"] = details[1]
        return jsonify(response)

@app.route("/beginVerification", methods=["POST"])
def checkAccount():
    """
    This function takes an email address and checks whether an account with this email already exists
    If it doesn't then a new one will be created.
    Then, a verification email will be sent to the provided email.
    """
    
    # Prepares response to be returned to the client
    response = {
        "userID" : None,
        "error" : None
    }
    
    # Attempts to convert POST request parameters from JSON to Python format
    email, name = None, None
    try:
        data = request.json
        email, name = data["email"], data["name"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    # Initalise a new User object
    account = User(email, name)
    if account.error is not None:
        # An error has occurred, add it to the response
        response["error"] = account.error
        return jsonify(response)
    
    # Initiate email verification
    verification = beginVerification(account.userID)
    
    if not verification[0]:
        # An error has occurred, return the error message
        response["error"] = verification[1]
        return jsonify(response)
    else:
        response["userID"] = account.userID
        return jsonify(response)
    
@app.route("/getAuthToken", methods=["POST"])
def checkCode():
    """
    This function takes a userID and verification code, and checks if the provided
    code is valid and not expired.
    If the code is valid, an AuthToken is returned.
    """
    
    # Prepares response to be returned to the client
    response = {
        "success" : False,
        "authToken" : None,
        "error" : None
    }
    
    # Only accept SSL connections as we are returning sensitive information
    """if not request.is_secure:
        response["error"] = "This service can only be accessed using SSL."
        return jsonify(response)"""
    
    # Attempts to convert POST request parameters from JSON to Python format
    userID, code = None, None
    try:
        data = request.json
        userID, code = data["userID"], data["code"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    verification = checkVerificationCode(userID, code)
    
    if verification[0]:
        # The verification has succeeded, generate a new AuthToken
        response["success"] = True
        
        # Returns plaintext authorisation token
        auth = getAuthToken(userID)
        
        if auth[0] is not None:
            response["authToken"] = auth[0]
        else:
            # An error has occurred
            response["success"] = False
            response["error"] = auth[1]
    else:
        # Verification failed, or an error occurred
        response["error"] = verification[1]
    
    return jsonify(response)

@app.route("/accountDetails", methods=["POST"])
def accountDetails():
    """
    This function takes a userID and authentication token. If authentication succeeds,
    the details for the provided userID will be returned.
    """
    
    # Prepares response to be returned to the client
    response = {
        "details": None,
        "error": None
    }
    
    userID, auth = None, None
    try:
        data = request.json
        userID, auth = data["userID"], data["authToken"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    authentication = authenticate(userID, auth)
    
    if authentication[0]:
        # Authentication has succeeded, obtain user details from userID
        temp_user = User(userID=userID)
        
        # Store user details in a record
        response["details"] = {
            "name": temp_user.name,
            "email": temp_user.email,
            "professional": bool(temp_user.professional),
            "verified": bool(temp_user.verified)
        }
        
        # Respond to the request
        return jsonify(response)
    else:
        # Authentication failed
        response["error"] = authentication[1]
        return jsonify(response)

@app.route("/makeReview", methods=["POST"])
def makeRestaurantReview():
    """
    This function allows users to make reviews for restaurants.
    """
    
    # Prepares response to be returned to the client
    response = {
        "success": None,
        "error": None
    }
    
    userID, token, restaurantID, rating, title, body = None, None, None, None, None, None
    try:
        data = request.json
        userID, token = data["userID"], data["authToken"]
        restaurantID = data["restaurantID"]
        rating, title, body = data["rating"], data["title"], data["body"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    review = makeReview(userID, token, restaurantID, rating, title, body)
    
    if not review[0]:
        # Error occurred
        response["success"] = False
        response["error"] = review[1]
    else:
        response["success"] = True
    
    return jsonify(response)

@app.route("/getReviews", methods=["POST"])
def getRestaurantReviews():
    """
    This function allows users to make reviews for restaurants.
    """
    
    # Prepares response to be returned to the client
    response = {
        "reviews": None,
        "error": None
    }
    
    restaurantID = None
    try:
        data = request.json
        restaurantID = data["restaurantID"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    reviews = getReviews(restaurantID)
    
    if reviews[0] is None:
        # Error occurred
        response["error"] = reviews[1]
    else:
        response["reviews"] = reviews[0]
    
    return jsonify(response)

@app.route("/changeEmail", methods=["POST"])
def changeUserEmail():
    """
    This function allows users to change the email address associated with
    their account.
    """
    
    # Prepares response to be returned to the client
    response = {
        "success": None,
        "error": None
    }
    
    userID, auth_token, new_email = None, None, None
    try:
        data = request.json
        userID, auth_token = data["userID"], data["authToken"]
        new_email = data["newEmail"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    temp_user = User(userID=userID)
    if temp_user.error != None:
        # An error has occured
        response["success"] = False
        response["error"] = temp_user.error
    else:
        # Attempt to change email
        print(new_email, auth_token)
        temp_user.changeEmail(new_email, auth_token)
        
        # Check for errors
        if temp_user.error != None:
            response["success"] = False
            response["error"] = temp_user.error
        else:
            response["success"] = True
    
    return jsonify(response)

@app.route("/restaurantSearch", methods=["POST"])
def searchForRestaurants():
    """
    This function allows users to provide a search term and returns a list of
    relevant restaurants (limited to 10 at most)
    """
    # Prepares response to be returned to the client
    response = {
        "results": None,
        "error": None
    }
    
    search_term = None
    try:
        data = request.json
        search_term = data["searchTerm"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    # Attempt to get relevant restaurants
    results = restaurantSearch(search_term)
    
    if results[0] is None:
        # An error has occurred
        response["error"] = results[1]
    else:
        # Restructure each tuple in the results into a dictionary
        results = results[0]
        for i in range(len(results)):
            restaurant = results[i]
            results[i] = {
                "restaurantID": restaurant[0],
                "name": restaurant[1]
            }
        
        response["results"] = results
    
    return jsonify(response)

@app.route("/reservationAvailability", methods=["POST"])
def getRestaurantAvailability():
    """
    This function allows users to get the available start times for reservations
    at a given restaurant on a given date for a specific number of people
    """
    # Prepares response to be returned to the client
    response = {
        "results": None,
        "error": None
    }
    
    restaurantID, date, persons = None, None, None
    try:
        data = request.json
        restaurantID = data["restaurantID"]
        date, persons = data["date"], data["persons"]
        # The date should be a string in format "YYYY-MM-DD" to comply with ISO 8601 
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    # Attempt to convert the date from string to datetime object
    dateObject = None
    try:
        dateObject = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as e:
        # A ValueError could be raised if the date is incorrectly formatted
        response["error"] = str(e)
        return jsonify(response)
    
    # Retrieve avaialble reservation start times
    availableReservations = getAvailableReservations(restaurantID, dateObject, persons)
    
    # Check for errors
    if availableReservations[0] is None:
        response["error"] = availableReservations[1]
        return jsonify(response)
    
    response["results"] = availableReservations[0]
    return jsonify(response)

@app.route("/makeReservation", methods=["POST"])
def placeReservation():
    """
    This function allows users to place reservations at a restaurant, and checks
    that the provided timeslot is available
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }
    
    userID, authToken, restaurantID, date, time, persons = None, None, None, None, None, None
    try:
        data = request.json
        userID, authToken = data["userID"], data["authToken"]
        restaurantID = data["restaurantID"]
        date, time, persons = data["date"], data["time"], data["persons"]
        # The date should be a string in format "YYYY-MM-DD" to comply with ISO 8601 
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    # Attempt to place reservation
    reservation = makeReservation(userID, authToken, restaurantID, date, time, persons)
    
    if not reservation[0]:
        # Reservation failed
        response["error"] = reservation[1]
    else:
        response["success"] = True
        
    return jsonify(response)

@app.route("/createRestaurant", methods=["POST"])
def createRestaurant():
    """
    This function allows users to be promoted to professional and create a 
    new blank restaurant
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }
    userID, authToken = None, None
    
    try:
        data = request.json
        userID, authToken = data["userID"], data["authToken"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    # Check that the provided authentication token is valid
    authentication = authenticate(userID, authToken)
    
    if not authentication[0]:
        response["error"] = authentication[1]
        return jsonify(response)
    
    # Authentication succeeded, promote the user
    _ = ProfessionalUser(userID=userID)
    
    response["success"] = True
    return jsonify(response)

@app.route("/updateRestaurant", methods=["POST"])
def changeRestaurantDetails():
    """
    This function allows users to change the details of restaurants which they manage
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }
    userID, authToken, restaurantName, description, category, location = None, None, None, None, None, None
    try:
        data = request.json
        userID, authToken = data["userID"], data["authToken"]
        restaurantName, description, category = data["restaurantName"], data["description"], data["category"]
        location = data["location"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
        
        # Stop execution here and return the error message
        return jsonify(response)
    
    restaurantUpdate = updateRestaurant(userID, authToken, restaurantName, description, category, location)
    response["success"] = restaurantUpdate[0]
    response["error"] = restaurantUpdate[1]
    
    return jsonify(response)

@app.route("/uploadRestaurantImage", methods=["POST"])
def uploadRestaurantImage():
    """
    This function allows an image to be uploaded to the user's restaurant
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }
    
    userID, authToken, image = None, None, None
    try:
        data = json.loads(request.form.to_dict()["data"])
        image = request.files["image"]
        userID = data["userID"]
        authToken = data["authToken"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        # An error could occur if the request is malformed
        response["error"] = "An unknown exception occured:", str(e)
    
    # Attempt to save the image to the filesystem
    saved = saveRestaurantImage(userID, authToken, image)
    
    response["success"] = saved[0]
    response["error"] = saved[1]
    
    return jsonify(response)

@app.route("/getRestaurantImages", methods=["POST"])
def retrieveRestaurantImages():
    """
    This function allows images for a given restaurant to be retrieved
    """
    # Prepares response to be returned to the client
    response = {
        "images": None,
        "error": None
    }

    restaurantID = None
    try:
        data = request.json
        restaurantID = data["restaurantID"]
    except KeyError:
        response["error"] = "Missing required parameter"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        response["error"] = "An unknown exception occured:", str(e)
        return jsonify(response)

    # Retrieve the images
    images = getRestaurantImages(restaurantID)

    # Insert the image dictionary to the response
    response["images"] = images

    return jsonify(response)

@app.route("/deleteRestaurantImage", methods=["POST"])
def removeRestaurantImage():
    """
    This function allows images for a given restaurant to be deleted
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }

    userID, authToken, imageName = None, None, None
    try:
        data = request.json
        userID, authToken = data["userID"], data["authToken"]
        imageName = data["imageName"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        response["error"] = "An unknown exception occured:", str(e)
        return jsonify(response)

    # Attempt to delete the image
    deleted = deleteRestaurantImage(userID, authToken, imageName)

    response["success"] = deleted[0]
    response["error"] = deleted[1]

    return jsonify(response)

@app.route("/addMenuItem", methods=["POST"])
def addRestaurantMenuItem():
    """
    This function allows users to add a new item to their restaurant's menu
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }

    userID, authToken, menuSection, name, description, calories, price = None, None, None, None, None, None, None
    changeExistingID = None
    try:
        data = request.json
        userID, authToken = data["userID"], data["authToken"]
        menuSection, name, description = data["menuSection"], data["name"], data["description"]
        calories, price = data["calories"], data["price"]
        changeExistingID = data["changeExistingID"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        response["error"] = "An unknown exception occured:", str(e)
        return jsonify(response)

    # Authenticate the user
    """authentication = authenticate(userID, authToken)
    if not authentication[0]:
        # Authentication failed
        response["error"] = authentication[1]
        return jsonify(response)"""

    # Authentication succeeded, check whether the user is a professional
    user = User(userID=userID)
    if not user.professional:
        # The user is not a professional, return an error
        response["error"] = "The specified user is not a professional user"
        return jsonify(response)

    # The user is a professional, so find their restaurantID
    user = ProfessionalUser(userID)
    restaurantID = user.restaurantID

    # Add the menu item
    added = None
    if changeExistingID is None:
        added = addMenuItem(restaurantID, menuSection, name, description, calories, price)
    else:
        added = changeMenuItem(restaurantID, menuSection, name, description, calories, price, changeExistingID)

    # Check for errors and store if necessary
    response["success"], response["error"] = added

    return jsonify(response)

@app.route("/deleteMenuItem", methods=["POST"])
def deleteRestaurantMenuItem():
    """
    This function allows users to delete an item from their restaurant's menu
    """
    # Prepares response to be returned to the client
    response = {
        "success": False,
        "error": None
    }

    userID, authToken, menuItemID = None, None, None
    try:
        data = request.json
        userID, authToken = data["userID"], data["authToken"]
        menuItemID = data["menuItemID"]
    except KeyError:
        response["error"] = "Missing required parameters"
        return jsonify(response)
    except ValueError:
        response["error"] = "Invalid data format"
        return jsonify(response)
    except Exception as e:
        response["error"] = "An unknown exception occured:", str(e)
        return jsonify(response)

    # Authenticate the user
    """authentication = authenticate(userID, authToken)
    if not authentication[0]:
        # Authentication failed
        response["error"] = authentication[1]
        return jsonify(response)"""

    # Authentication succeeded, check whether the user is a professional
    user = User(userID=userID)
    if not user.professional:
        # The user is not a professional, return an error
        response["error"] = "The specified user is not a professional user"
        return jsonify(response)

    # The user is a professional, so find their restaurantID
    user = ProfessionalUser(userID)
    restaurantID = user.restaurantID

    # Delete the menu item
    deleted = deleteMenuItem(menuItemID, restaurantID)

    # Check for errors and store if necessary
    response["success"], response["error"] = deleted

    return jsonify(response)

# This runs the app so that POST requests can be received
if __name__ == "__main__":
    app.run(host="localhost", port=8080)