import React, { useState, useEffect } from 'react';
import { FaLocationArrow } from 'react-icons/fa';
import "./Home.css";

function LocationPicker({ latitude, setLatitude, longitude, setLongitude }) {
	// This component is a button which allows the user to give access to their precise location
	const [cityName, setCityName] = useState("No location found");

	function getCityName() {
		// This function attempts to find the name of the user's city for displaying on the home page
		if (navigator.geolocation) {
			// Request the user's current coordinates for the user
			navigator.geolocation.getCurrentPosition(async function(position) {
				setLatitude(position.coords.latitude);
				setLongitude(position.coords.longitude);
	
				try {
					// Fetch location data from OpenStreetMap API and then serialise it as JSON
					const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`);
					const data = await response.json();

					// Sometimes there is no city or town available, so we must check if it is available before using it
					// This uses city -> town -> municipality in order of priority
					if (data.address) {
						if (data.address.city) {
							setCityName(data.address.city);
						} else if (data.address.town) {
							setCityName(data.address.town);
						} else if (data.address.municipality) {
							setCityName(data.address.municipality);
						}
					}
				} catch (error) {
					console.error(error);
				}
			}, function(error) {
				console.error(error);
			});
		}
	}

	// Initialise location upon opening the web app
	getCityName();

  	return (
		<div className="locationPicker" onClick={getCityName}>
			<FaLocationArrow className="locationArrow" />
			<t>{cityName}</t>
		</div>
	);
}

function Restaurant({ restaurantID, setPage }) {
	// This function retrieves data about the restaurant
	async function getRestaurantData(restaurantID) {
		// Make a POST request to the backend to retrieve restaurant data
		const response = await fetch('https://localhost:8080/restaurantDetails', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				restaurantID: restaurantID,
			}), 
		});

		// Decode the response as JSON
		const data = await response.json();

		// Check for errors
		if (data.error) {
			// Throw an error if there is one
			throw new Error(data.error);
		} else {
			// Return the restaurant data
			return data.details;
		}
	}

	// This function retrieves the image for the restaurant
	async function getRestaurantImage(restaurantID) {
		// Make a POST request to the backend to retrieve restaurant images
		const response = await fetch('https://localhost:8080/getRestaurantImages', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				restaurantID: restaurantID,
			}),
		});

		// Decode the response as JSON
		const data = await response.json();
		// The returned data is in JSON format with an array of images stored in base64 format
		// The first image is the restaurant image, so we can simply return that
		if (data.error) {
			throw new Error(data.error);
		} else {
			// The images are stored in a dictionary, so return the first value of the dictionary
			return Object.values(data.images)[0];
		}
	}

	// This component displays a single restaurant
	// Retrieve restaurant data from the backend, catching any errors
	const [restaurantData, setRestaurantData] = useState([]);
	const [restaurantImage, setRestaurantImage] = useState(null);
	const [error, setError] = useState(null); 

	// Retrieve restaurant data when the component is first rendered
	useEffect(() => {
		async function fetchRestaurantDetails() {
			// Retrieve restaurant data
			try {
				const data = await getRestaurantData(restaurantID);
				const image = await getRestaurantImage(restaurantID);
	
				setRestaurantData(data);
				setRestaurantImage(image);
				setError(null); // Clear any previous errors
			} catch (error) {
				setError(error);
			}
		}

		fetchRestaurantDetails();
	}, [restaurantID]); // This function runs when the restaurantID is set

	// If an error occurred, display it
	if (error) {
		return <div className="restaurantContainer">Error getting restaurant {restaurantID} details: {error.message}</div>
	} else {
		return (
			<div className="restaurantContainer" onClick={() => setPage("viewRestaurantDetails:" + restaurantID)}>
				<div>
					<t className="restaurantName">{restaurantData.name}</t>
				</div>
				<div>
					<t className="restaurantDescription">{restaurantData.description}</t>
				</div>
				<div className="restaurantImageContainer">
					<img className="restaurantImage" src={`data:image/jpeg;base64,${restaurantImage}`} />
				</div>
			</div>
		);
	}
}

function RestaurantList({ latitude, longitude, setPage, searchResults, searchError }) {
	// This function retrieves restaurant data from the backend and displays it
	// Initialise state variable for storing restaurant data
	const [restaurants, setRestaurants] = useState([]);
	const [error, setError] = useState(null);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		async function retrieveRestaurants(latitude, longitude, random=false) {
			// Make a POST request to the backend to retrieve restaurant data
			const response = await fetch("https://localhost:8080/nearbyRestaurants", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					latitude: latitude || null, // If latitude is undefined, set it to null
					longitude: longitude || null,
					random: random,
				}),
			});

			// Decode the response as JSON
			const data = await response.json();
			// Check for errors
			if (data.error) {
				// Throw an error if there is one
				setError(Error(data.error));
			} else {
				// Return the restaurant data 
				setError(null); // Clear any previous errors
				setRestaurants(data.restaurants);
			}
		}

		retrieveRestaurants(latitude, longitude, !(latitude && longitude))
			.then(() => setIsLoading(false))

	}, [latitude, longitude]) // This function runs when the latitude or longitude changes

	// This component displays a list of nearby restaurants, or random restaurants if no location is available
	// If an error is stored, display it
	if (error) {
		return <p>Error finding nearby restaurants: {error.message}</p>
	} else if (isLoading) {
		return <p>Loading...</p>
	} else if (searchError) {
		return <p>Error searching for restaurants: {searchError.message}</p>
	} else if (searchResults && searchResults.length > 0) {
		return (
			<div>
				{
					// Display each restaurant in the list
					searchResults.map((restaurant) => (
						<Restaurant
							restaurantID={restaurant.restaurantID}
							setPage={setPage}
						/>
					)) 
				}
			</div>
		);
	} else {
		// if the array contains subarrays, extract the restaurantID from each subarray
		if (restaurants.length > 0 && restaurants[0] instanceof Array) {
			// Iterate through and change each subarray to just the restaurantID
			setRestaurants(restaurants.map((restaurant) => restaurant[0]));
		}
		return (
			<div> 
				{
					// Display each restaurant in the list
					restaurants.map((restaurant) => (
						<Restaurant
							restaurantID={restaurant}
							setPage={setPage}
						/>
					)) 
				}
			</div>
		);
	}
}

function RestaurantSearchBar({ setSearchResults, setSearchError }) {
	// Store the search term in a state variable
	const [searchTerm, setSearchTerm] = useState("");

	// Retrieve search results from the backend when the search term changes
	useEffect(() => {
		async function retrieveSearchResults(searchTerm) {
			// If no search term is provided, return an empty array
			if (searchTerm.length == 0) {
				return { results: [] };
			}

			// Make a POST request to the backend to retrieve restaurant data
			const response = await fetch("https://localhost:8080/restaurantSearch", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					searchTerm: searchTerm,
				}),
			});
			
			// Decode the response as JSON
			const data = await response.json();
			// Check for errors
			if (data.error) {
				// Throw an error if there is one - this will be displayed
				throw new Error(data.error);
			} else {
				// Return the restaurants to be stored in the state variable
				return data;
			}
		}
		retrieveSearchResults(searchTerm)
			.then((data) => setSearchResults(data.results))
			.catch((error) => setSearchError(error));
	}, [searchTerm]);

	return (
		<div>
			<input className="searchBar" type="search" placeholder="Search" onChange={(event) => setSearchTerm(event.target.value)} />
		</div>
	);
}

export default function Home({ setPage }) {
	// Initialise state variables for storing user location data
	const [latitude, setLatitude] = useState(null);
	const [longitude, setLongitude] = useState(null);

	// State variable for storing search results for restaurants
	const [searchResults, setSearchResults] = useState([]);
	const [searchError, setSearchError] = useState(null);

    return (
      	<div className="homeBody">
        	<t className="homeTitle">Restaurants near you</t>
        	<LocationPicker latitude={latitude} setLatitude={setLatitude} longitude={longitude} setLongitude={setLongitude}/>
			<RestaurantSearchBar setSearchResults={setSearchResults} setSearchError={setSearchError}/>
			<RestaurantList latitude={latitude} longitude={longitude} setPage={setPage} searchResults={searchResults} searchError={searchError}/>
     	</div>
    );
}