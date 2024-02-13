import React, { useState, useEffect } from 'react';
import "./PlaceReview.css";

function ReviewForm({ restaurantID, backPage, userID, authToken}) {
    // State variables for the review form
    const [title, setTitle] = useState("");
    const [body, setBody] = useState("");
    const [rating, setRating] = useState(5);
    const [reviewError, setReviewError] = useState(null);

    async function submitReview() {
        // Reset any stored errors from previous attempts
        setReviewError(null);

        // Make a request with the review and rating
        const response = await fetch('https://localhost:8080/makeReview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                restaurantID: restaurantID,
                title: title,
                body: body,
                rating: rating
            })
        });

        // Decode the response as JSON
        const data = await response.json();

        // Check for errors
        if (data.error) {
            // Set the error message
            setReviewError(data.error);
        } else {
            // The request succeeded, so move back to the restaurant details page
            backPage();
        }
    }

    return (
        <div className="reviewForm">
            <h1>Place a Review</h1>
            {reviewError != null && <p>{reviewError}</p>}
            <h3>Rating:</h3>
            <select value={rating} onChange={(r) => setRating(r.target.value)}>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
            </select>
            <h3>Review title:</h3>
            <input type="text" value={title} onChange={(t) => setTitle(t.target.value)} />
            <h3>Body:</h3>
            <textarea value={body} onChange={(b) => setBody(b.target.value)} className="reviewBody" />
            <button onClick={submitReview}>Submit</button>
        </div>
    );
}

export default function PlaceReview({ restaurantID, setPage, backPage }) {
    // Check that the user is signed in before allowing them to place a review
    let userID, authToken;
    try {
        userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
        authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];
    } catch {
        // If the cookies are not present, the user is not signed in
        setPage("signIn");
    }
    return (
        <>
            <button className="backButton" onClick={() => backPage()}>Back</button>
            <ReviewForm restaurantID={restaurantID} backPage={backPage} userID={userID} authToken={authToken} />
        </>
    );
}