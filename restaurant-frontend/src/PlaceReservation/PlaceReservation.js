import React, { useState, useEffect } from 'react';
import "./PlaceReservation.css";

// This component displays all of the available reservation times for a given restaurant
function ReservationPane({ restaurantID, setPage, userID, authToken }) {
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]); // stores the selected date
    const [times, setTimes] = useState([]); // stores the available reservation times for the selected date
    const [persons, setPersons] = useState(2); // stores number of persons for the reservation
    const [reservationError, setReservationError] = useState(null); // stores any error message returned by the server

    // Creates an effect so that available times are refreshed when the date changes
    useEffect(() => {
        async function fetchAvailableTimes() {
            // Reset the stored error and times
            setReservationError(null);
            setTimes([]);
            // Send a request to the server to get the available reservation times for the given restaurant and date
            const response = await fetch("https://localhost:8080/reservationAvailability", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    restaurantID: restaurantID,
                    date: date,
                    persons: persons
                })
            });
            // Decode the response as JSON
            const data = await response.json();
            if (data.error) {
                setReservationError(data.error);
            } else {
                setTimes(data.results);
            }
        }
        fetchAvailableTimes();
    }, [date, persons]);

    // Iterate through each available time and create a new ReservationOption component for each
    return (
        <div className="reservationPane">
            {reservationError != null && <p>{reservationError}</p>}
            <input type="date" value={date} onChange={(d) => setDate(d.target.value)} />
            <select value={persons} onChange={(p) => setPersons(p.target.value)}>
                <option value="1">1 person</option>
                <option value="2">2 people</option>
                <option value="3">3 people</option>
                <option value="4">4 people</option>
                <option value="5">5 people</option>
                <option value="6">6 people</option>
            </select>
            {times.map((time) => 
                <ReservationOption 
                time={time} date={date} restaurantID={restaurantID}
                persons={persons} userID={userID} authToken={authToken}
                setPage={setPage} setReservationError={setReservationError} 
                />
            )}
            {times.length == 0 && <p>Sorry, no available reservation slots found...</p>}
        </div>
    );
}

// This function allows the user to select and place a reservation for each time
function ReservationOption({ time, date, restaurantID, persons, userID, authToken, setPage, setReservationError }) {
    function placeReservation() {
        // This function sends a request to the server to place a reservation with the given details
        fetch ("https://localhost:8080/makeReservation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                restaurantID: restaurantID,
                date: date,
                time: time,
                persons: persons,
                userID: userID,
                authToken: authToken
            })
        }).then(response => response.json()).then(data => {
            if (data.error) {
                setReservationError(data.error);
            } else {
                setPage("home"); // no error occurred, so return to the home page
            }
        });
    }

    return (
        <div className="reservationOption">
            <h4>Reservation at {time}</h4>
            <div>
                <p>{persons} people</p>
                <p>{date}</p>
            </div>
            <button onClick={placeReservation}>Book</button>
        </div>
    );
}

export default function PlaceReservation({ restaurantID, setPage, backPage }) {
    // Check that the user is signed in before allowing them to place a reservation
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
            <h1>Reservation availability</h1>
            <ReservationPane restaurantID={restaurantID} setPage={setPage} userID={userID} authToken={authToken} />
        </>
    );
}