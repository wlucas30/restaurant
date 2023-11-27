from services.authenticate import authenticate
from models.user import User, ProfessionalUser
import os

# This constant stores the location of the image store
imageStore = "/Users/wl/Documents/restaurant/server/static/restaurant_images"

# This function allows a saved restaurantImage to be deleted from the filesystem
def deleteRestaurantImage(userID, authToken, imageName):
    # First authenticate the provided authentication token
    """authentication = authenticate(userID, authToken)
    if not authentication[0]:
        # Authentication failed
        return (False, authentication[1])
    """
    # Check that the user is a professional and get their restaurantID
    restaurantID = None
    user = User(userID=userID)
    if not user.professional:
        # The user does not own a restaurant, return an error
        return (False, "The specified user is not a professional user")
    else:
        # Retrieve the user's restaurantID
        user = ProfessionalUser(user.userID)
        restaurantID = user.restaurantID

    # Check that an image exists with the given name
    filepath = imageStore + "/" + str(restaurantID)
    if not os.path.isdir(filepath):
        # The restaurant directory does not exist, return an error
        return (False, "The image name could not be found")
    else:
        # The restaurant directory exists, check if the image exists
        if not os.path.isfile(filepath+"/"+imageName+".jpg"):
            # The image does not exist, return an error
            return (False, "The image name could not be found")

    # The image exists, so delete it
    try:
        os.remove(filepath+"/"+imageName+".jpg")
    except Exception as e:
        # An error occurred deleting the image
        return (False, f"An error occurred deleting the image: {e}")

    # Decrement each image name by 1 where the image number is greater than the deleted image
    for image in os.listdir(filepath):
        # Check if the image is greater than the deleted image
        if int(image[:-4]) > int(imageName):
            # The image is greater than the deleted image, so decrement the image name by 1
            os.rename(filepath+"/"+image, filepath+"/"+str(int(image[:-4])-1)+".jpg")

    # The image has been deleted
    return (True, None)