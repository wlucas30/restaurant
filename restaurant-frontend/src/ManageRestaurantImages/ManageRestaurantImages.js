import React, { useState, useEffect } from 'react';
import "./ManageRestaurantImages.css";

function RestaurantImagesPane({ userID, authToken, restaurantID }) {
    // State variable for storing all of the restaurant's images
    const [images, setImages] = useState(null);
    const [imageError, setImageError] = useState(null);
    const [image, setImageFile] = useState(null); // image to be uploaded

    // Effect which retrieves stored images once the restaurantID is provided
    useEffect(() => {
        async function getImages() {
            const response = await fetch("https://localhost:8080/getRestaurantImages", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    restaurantID: restaurantID
                })
            });
            const data = await response.json();
            if (data.error) {
                setImageError(data.error);
            } else {
                setImages(data.images);
            }
        }
        getImages();
    }, [restaurantID, images]);

    async function uploadNewImage() {
        // Clear any previous errors
        setImageError(null);

        // Check that an image has been selected
        if (!image) {
            setImageError("No image selected");
            return;
        }

        // Send a request to the server to upload the new image
        const formData = new FormData();
        formData.append("data", JSON.stringify({
            userID: userID,
            authToken: authToken,
        }));
        formData.append("image", image);
        const response = fetch("https://localhost:8080/uploadRestaurantImage", {
            method: "POST",
            body: formData
        });
        response.then(data => data.json()).then(data => {
            if (data.error) {
                setImageError(data.error);
            } else {
                // Update the images state variable to trigger a re-fetch of the images
                const newImages = structuredClone(images);
                newImages["0"] = "refresh"; // this is a dummy value to trigger a re-fetch
                setImages(newImages);
            }
        });
    }

    // The images are stored in a dictionary where the key is their image name
    // Create an array of components to display the images
    const imageComponents = [];
    if (images) {
        for (const imageName in images) {
            // Only create a component if the imageName can be parsed as an integer
            if (parseInt(imageName)) {
                imageComponents.push(<RestaurantImageFrame imageName={imageName} image={images[imageName]} 
                userID={userID} authToken={authToken} 
                images={images} setImages={setImages} />);
            }
        }
    }

    return (
        <div className="restaurantImagesPane">
            <h2>Existing restaurant images</h2>
            <p>{imageError}</p>
            <div className="existingImagesContainer">
            {imageComponents.length > 0 ? imageComponents : <p>No images currently stored</p>}
            </div>
            <div className="newImagesContainer">
                <h2>Upload new image</h2>
                <input type="file" onChange={(f) => setImageFile(f.target.files[0])} /><br />
                <button onClick={uploadNewImage}>Upload</button>
            </div>
        </div>
    );
}

function RestaurantImageFrame({ userID, authToken, imageName, image, images, setImages }) {
    // State variable for storing any errors that occur when deleting an image
    const [deleteError, setDeleteError] = useState(null);

    async function deleteImage() {
        // Clear any previous errors
        setDeleteError(null);

        // Send a request to the server to delete the image
        const response = await fetch("https://localhost:8080/deleteRestaurantImage", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                imageName: imageName,
            })
        });
        
        // Convert the response to JSON and handle any errors
        const data = await response.json();
        if (data.error) {
            setDeleteError(data.error);
        } else {
            // Update the images state variable to trigger a re-render
            const newImages = structuredClone(images);
            delete newImages[imageName];
            setImages(newImages);
        }
    }

    return (
        <div className="restaurantImageFrame">
            <img src={`data:image/jpeg;base64,${image}`} alt="Restaurant image" className="restaurantImage" />
            <button onClick={deleteImage}>Delete</button>
        </div>
    );
}

export default function ManageRestaurantImages({ setPage, backPage }) {
        // Check that the user is signed in before allowing restaurant image changes
        let userID, authToken;
        try {
            userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
            authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];
        } catch {
            // If the cookies are not present, the user is not signed in
            backPage();
        }
    
        // Fetch the user's restaurantID on component load
        const [restaurantID, setRestaurantID] = useState(null);
        useEffect(() => {
            async function getRestaurantID() {
                const response = await fetch("https://localhost:8080/getRestaurantID", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        userID: userID,
                    })
                })
                const data = await response.json();
                if (data.error) {
                    // The user does not have a restaurant, so they cannot access the control panel
                    backPage();
                } else {
                    setRestaurantID(data.restaurantID);
                }
            }
            getRestaurantID()
        }, []);
    
        return (
            <>
                <button className="backButton" onClick={backPage}>Go back</button>
                <RestaurantImagesPane restaurantID={restaurantID} userID={userID} authToken={authToken} />
            </>
        );
}