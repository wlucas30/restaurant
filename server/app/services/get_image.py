import base64
import os

# This function returns all the images for a given restaurant
def getRestaurantImages(restaurantID):
    # Check that the restaurantID is an integer
    if type(restaurantID) is not int:
        return {}

    imageStore = "/Users/wl/Documents/restaurant/server/static/restaurant_images"
    # Check if any images exist for the given restaurant
    filepath = imageStore + "/" + str(restaurantID)

    if not os.path.isdir(filepath):
        # No images exist for the given restaurant, return an empty dictionary
        return {}

    # Iterate through each image stored in the restaurant's directory
    images = {}
    for imageName in os.listdir(filepath):
        # Open the image and encode it as base64
        with open(filepath+"/"+imageName, "rb") as imageFile:
            # Store the base64 encoded image in the dictionary with the image name as the key
            # Remove the .jpg suffix from the image name
            imageName = imageName[:-4]
            # Images are encoded in utf-8 to allow them to be stored in JSON
            images[imageName] = base64.b64encode(imageFile.read()).decode("utf-8")
    return images