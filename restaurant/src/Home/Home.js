import React, { useState } from 'react';
import { FaLocationArrow } from 'react-icons/fa';
import "./Home.css";

var latitude;
var longitude;

function LocationPicker() {
	// This component is a button which displays the user's predicted location and
	// allows the user to give access to their precise location
	const [cityName, setCityName] = useState("No location found");

	function getCityName() {
		// This function attempts to find the name of the user's city for displaying on the home page
		if (navigator.geolocation) {
			// Request the user's current coordinates for the user
			navigator.geolocation.getCurrentPosition(async function(position) {
				latitude = position.coords.latitude;
				longitude = position.coords.longitude;
	
				try {
					// Fetch location data from OpenStreetMap API and then serialise it as JSON
					const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`);
					const data = await response.json();

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

function Restaurant({ restaurantName, restaurantDescription, imageName }) {
	return (
		<div className="restaurantContainer">
			<div>
				<t className="restaurantName">{restaurantName}</t>
			</div>
			<div>
				<t className="restaurantDescription">{restaurantDescription}</t>
			</div>
			<div className="restaurantImageContainer">
				<img className="restaurantImage" src={require("../Assets/".concat(imageName))} alt="Image of restaurant" />
			</div>
		</div>
	);
}

function RestaurantList() {
	// This component displays a list of nearby restaurants
	return (
		<div>
			<Restaurant restaurantName="Will's Kitchen" restaurantDescription="0.25 miles away" imageName="1.jpeg" />
			<Restaurant restaurantName="Savory Haven Grill" restaurantDescription="2.3 miles away" imageName="2.jpeg" />
		</div>
	);
}

export default function Home() {
    return (
      	<div className="homeBody">
        	<t className="homeTitle">Restaurants near you</t>
        	<LocationPicker />
			<RestaurantList />
     	</div>
    );
}