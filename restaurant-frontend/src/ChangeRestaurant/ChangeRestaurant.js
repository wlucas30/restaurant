import React, { useState, useEffect, Component } from 'react';
import "./ChangeRestaurant.css";
import GoogleMapReact from 'google-map-react';

function LocationMap({ position, setPosition }) {
    const coords = {lat: parseFloat(position.split(", ")[0]), lng: parseFloat(position.split(", ")[1])};
    let marker;
    function apiIsLoaded(map, maps) {
        // Get the restaurant location from the form
        const restaurantLocation = coords;
        // Create a marker on the map
        marker = new maps.Marker({
            position: restaurantLocation,
            map,
            title: 'Restaurant location',
            draggable: true,
        });

        // Add a listener for the dragend event (marker is moved by the user)
        marker.addListener('dragend', function() {
            // Finding the new position of the marker
            const newPosition = marker.getPosition();
            const lat = newPosition.lat();
            const lng = newPosition.lng();
            setPosition(lat + ", " + lng);
        });
    }

    const defaultProps = {
      center: coords,
      zoom: 13
    };
  
    return (
        <div style={{ height: '60vh', width: '50%' }}>
            <GoogleMapReact
                bootstrapURLKeys={{ key: process.env.GOOGLE_MAPS_API_KEY }}
                defaultCenter={defaultProps.center}
                defaultZoom={defaultProps.zoom}
                yesIWantToUseGoogleMapApiInternals
                onGoogleApiLoaded={({ map, maps }) => {
                    apiIsLoaded(map, maps)
                }}
            />
        </div>
    );
}

function RestaurantDetailsForm({ restaurantID, userID, authToken }) {
    // Store state variables for the contents of the form
    const [restaurantName, setRestaurantName] = useState(null);
    const [restaurantDescription, setRestaurantDescription] = useState(null);
    const [restaurantLocation, setRestaurantLocation] = useState(null);
    const [restaurantCategory, setRestaurantCategory] = useState(null);
    const [restaurantError, setRestaurantError] = useState(null);

    // Fetch the restaurant details from the backend on component load and populate the form
    useEffect(() => {
        async function getRestaurantDetails() {
            const response = await fetch("https://localhost:8080/restaurantDetails", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    restaurantID: restaurantID,
                })
            })
            const data = await response.json();
            if (data.error) {
                // The restaurant details could not be fetched
                setRestaurantError(data.error);
            } else {
                setRestaurantName(data.details.name);
                setRestaurantDescription(data.details.description);
                setRestaurantLocation(data.details.location);
                setRestaurantCategory(data.details.category);
            }
        }
        getRestaurantDetails()
    }, [restaurantID]); // does not run until restaurantID is provided

    // This is executed when the form is submitted
    function submitData() {
        // Clear any previous errors
        setRestaurantError(null);

        // Send a request to the server to change the restaurant's details
        const response = fetch("https://localhost:8080/updateRestaurant", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                restaurantName: restaurantName,
                description: restaurantDescription,
                location: restaurantLocation,
                category: restaurantCategory
            })
        });
        response.then(data => data.json()).then(data => {
            if (data.error) {
                setRestaurantError(data.error);
            }
        });
    }

    return (
        <div className="restaurantDetailsForm">
            <h2>Change restaurant details</h2>
            {restaurantError && <p>{restaurantError}</p>}
            <input type="text" value={restaurantName} 
            onChange={n => setRestaurantName(n.target.value)} placeholder="Restaurant name" />
            <textarea type="text" className="description" value={restaurantDescription} 
            onChange={d => setRestaurantDescription(d.target.value)} placeholder="Description" />
            <input type="text" value={restaurantCategory} 
            onChange={c => setRestaurantCategory(c.target.value)} placeholder="Category" />

            {restaurantLocation !== null &&
            <LocationMap position={restaurantLocation} setPosition={setRestaurantLocation} />}<br />

            <button onClick={submitData}>Submit new details</button>
        </div>
    );
}

export default function ChangeRestaurantDetails({ setPage, backPage }) {
    // Check that the user is signed in before allowing restaurant detail changes
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
            <RestaurantDetailsForm restaurantID={restaurantID} userID={userID} authToken={authToken} />
        </>
    );
}