from services.authenticate import authenticate
from models.user import User, ProfessionalUser
import magic
from PIL import Image
import os

# This constant stores the location of the image store
imageStore = "/Users/wl/Documents/restaurant/server/static/restaurant_images"

# This function allows an uploaded restaurantImage to be saved to the filesystem
def saveRestaurantImage(userID, authToken, image):
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
    
    # Authentication has succeeded and the restaurantID has been retrieved, now validate the image
    validation = validateImage(image)
    
    if validation[0] is None:
        # Validation failed, return the error message
        return (False, validation[1])
    
    # Validation succeeded, now save the image
    image = validation[0]
    
    number_images = 0
    filepath = imageStore + "/" + str(restaurantID)
    # Check if the restaurant directory already exists
    if os.path.isdir(filepath):
        # The directory exsists, check how many images are stored to determine filename
        number_images = len(os.listdir(filepath))
    else:
        # The directory does not exist, so no images are stored
        number_images = 0
        
        # Make a new directory for storing the image
        os.mkdir(filepath)
    
    # The image name should be a number 1 greater than the current amount of images
    filename = str(number_images + 1) + ".jpg"
    
    # Try to save the image
    try:
        image.save(filepath+"/"+filename, format="JPEG")
    except Exception as e:
        # An error occurred saving the image
        return (False, f"An error occurred saving the image: {e}")
    
    # Return success message
    return (True, None)
    
# This function validates a provided image
def validateImage(image):
    # Maximum file size is 5MB (5 * 10^6 bytes)
    max_filesize = 5 * (10 ** 6)
    
    # Check file size
    if len(image.read()) > max_filesize:
        return (None, "The provided image file must not exceed 5MB")
    
    image.seek(0) # This moves the cursor to the beginning of the image file
    
    # Now check the MIME type of the image
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(image.read())
    
    # Check that the MIME type is an image
    if not file_mime_type.startswith("image"):
        return (None, "The provided image is incorrectly formatted")
    
    # Now remove the metadata from the image
    image = Image.open(image)
    image_metadata_removed = image.copy()
    image_metadata_removed.info = {}
    
    # Now return the image with no error
    return (image_metadata_removed, None)