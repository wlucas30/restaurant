from flask import Flask, request, jsonify
from services.nearby_restaurants import getNearbyRestaurants, getRandomRestaurants
from services.restaurant_details import getRestaurantDetails
from services.email_verification import beginVerification
from services.check_verification import checkVerificationCode
from services.auth_token import getAuthToken
from services.authenticate import authenticate
from services.make_review import makeReview
from services.get_reviews import getReviews
from models.user import User

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
        "success" : False,
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
        response["success"] = True
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

# This runs the app so that POST requests can be received
if __name__ == "__main__":
    app.run(host="localhost", port=8080)