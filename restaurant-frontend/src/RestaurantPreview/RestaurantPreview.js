import React, { useState, useEffect } from 'react';
import "./RestaurantPreview.css";
import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";
import Slider from "react-slick";

function RestaurantDetailsPane({ restaurantID }) {
    // State variables for the restaurant details
    const [restaurantName, setRestaurantName] = useState(null);
    const [restaurantDescription, setRestaurantDescription] = useState(null);
    const [restaurantCategory, setRestaurantCategory] = useState(null);
    const [restaurantOpeningPeriods, setRestaurantOpeningPeriods] = useState(null);
    const [restaurantDetailsError, setRestaurantDetailsError] = useState(null);

    // Fetch the restaurant details from the backend
    useEffect(() => { // the useEffect ensures that the fetch is only performed once
        fetch('https://localhost:8080/restaurantDetails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ restaurantID: restaurantID })
        })
            .then(response => response.json()) // parse the response as JSON
            .then(data => {
                if (data.error) {
                    setRestaurantDetailsError(data.error); // this will be displayed
                } else {
                    setRestaurantName(data.details.name);
                    setRestaurantDescription(data.details.description);
                    setRestaurantCategory(data.details.category);
                    setRestaurantOpeningPeriods(data.details.openingPeriods);
                }
            });
    }, []);

    // Display the restaurant details
    if (restaurantDetailsError) {
        return <p>{restaurantDetailsError}</p>
    } else if (restaurantName && restaurantDescription && restaurantCategory && restaurantOpeningPeriods) {
        return (
            <div className="restaurantDetailsPane">
                <h1>{restaurantName}</h1>
                <p>{restaurantDescription}</p>
                <p><strong>Category:</strong> {restaurantCategory}</p>
                <h2>Opening Hours</h2>
                {
                    // Iterate through the opening periods description and display each one
                    describeOpeningPeriods(restaurantOpeningPeriods).map((period) => (
                        <p style={{margin:0}}>{period}</p>
                    ))
                }
            </div>
        );
    } else {
        return <p>Loading...</p>;
    }
}

function describeOpeningPeriods(openingPeriods) {
    // This function takes a list of opening periods and returns a string describing them
    // The opening periods are in the format:
    // "1: 10:00-14:00, 2: 17:00-22:00, 3: 10:00-13:00" with each day of the week separated by a comma

    // Split the opening periods into a list of days
    const days = openingPeriods.split(", ");
    let orderedDays = new Array(days.length);

    // Iterate through each day
    for (let i = 0; i < days.length; i++) {
        // Split the day into the day number and the opening hours
        const day = days[i];

        // Convert the day number into a weekday
        const dayNumber = day[0];
        const dayName = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][dayNumber-1];

        // Replace the day number and opening hours with the weekday and opening hours
        orderedDays[i] = dayName + ": " + day.substring(2);
    }

    // Return the array of days
    return orderedDays
}

function RestaurantImageCarousel({ restaurantID }) {
    // State variables for storing the restaurant images
    const [restaurantImages, setRestaurantImages] = useState([]);
    const [restaurantImagesError, setRestaurantImagesError] = useState(null);

    // Fetch the restaurant images from the backend
    useEffect(() => {
        async function getRestaurantImages() {
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
            console.log(data.images);
            // The returned data is in JSON format with an array of images stored in base64 format
            if (data.error) {
                throw new Error(data.error);
            } else {
                // The images are stored in a dictionary, so move them to an array to disregard keys
                let imagesArray = [];
                for (let key in data.images) {
                    // Only add to the array where the key is a valid integer
                    if (Number.isInteger(parseInt(key))) {
                        imagesArray.push(data.images[key]);
                    }
                }
                return imagesArray;
            }
        }

        getRestaurantImages()
            .then(images => {
                setRestaurantImages(images);
            })
            .catch(error => {
                setRestaurantImagesError(error);
            });
    }, []);

    // Display the restaurant images in a carousel
    if (restaurantImagesError) {
        return <p>Error occurred retrieving images: {restaurantImagesError}</p>
    } else if (restaurantImages.length > 0) {
        return (
            <Slider slidesToShow={1} infinite={false} dots={true} adaptiveHeight={true} className="imageCarousel">
                {
                    restaurantImages.map((image) => (
                        <img
                            src={`data:image/jpeg;base64,${image}`}
                            alt="Restaurant image" 
                        />
                    ))
                }
            </Slider>
        );
    }
}

function Review({ review }) {
    return (
        <div className="review">
            <h3>{review.title}</h3>
            <h5>Rating: {review.rating}/5</h5>
            <p>{review.body}</p>
            <hr />
        </div>
    );
}

function RestaurantReviewList({ restaurantID, setPage }) {
    // State variables for storing all of the fetched reviews
    const [reviews, setReviews] = useState([]);
    const [reviewsError, setReviewsError] = useState(null);

    // Fetch the reviews from the backend
    useEffect(() => {
        async function getRestaurantReviews() {
            // Make a POST request to the backend to retrieve restaurant reviews
            const response = await fetch('https://localhost:8080/getReviews', {
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
            if (data.error) {
                throw new Error(data.error);
            } else {
                return data.reviews;
            }
        }
        getRestaurantReviews()
            .then(reviews => {
                setReviews(reviews);
            })
            .catch(error => {
                setReviewsError(error);
            });
    }, []);

    if (reviewsError) {
        return <p>Error occurred fetching reviews</p>
    } else {
        return (
            <div className="reviewPane">
                <h2>Reviews</h2>
                <button onClick={() => setPage("placeReview:" + restaurantID)}>Place review</button>
                <hr />
                {
                    reviews.map((review) => (
                        <Review review={review} />
                    ))
                }
            </div>
        );
    }
}

function RestaurantBookingOptionsPane({ restaurantID, setPage }) {
    return (
        <div className="bookingOptions">
            <button onClick={() => setPage("placeReservation:" + restaurantID)}>Make Reservation</button><br />
            <button onClick={() => setPage("placeFoodOrder:" + restaurantID)}>Order Food</button>
        </div>
    );
}

export default function RestaurantPreview({ restaurantID, setPage }) {
    // This is the root component for the restaurant preview page
    return (
        <>
            <button className="backButton" onClick={() => setPage("home")}>Back</button>
            <RestaurantDetailsPane restaurantID={restaurantID} />
            <RestaurantImageCarousel restaurantID={restaurantID} />
            <RestaurantBookingOptionsPane restaurantID={restaurantID} setPage={setPage} />
            <RestaurantReviewList restaurantID={restaurantID} setPage={setPage} />
        </>
    );
}