import React, { useState, useEffect } from 'react';
import "./ViewReservations.css";

function ReservationsPane({ userID, authToken }) {
    const [selectedDate, setSelectedDate] = useState(new Date()); // Stores selected date, default is today
    const [reservations, setReservations] = useState([]); // Stores the reservations for the selected date
    const [error, setError] = useState(null); // Stores any error message

    // This method is called when the date is changed
    useEffect(() => {
        async function getReservations() {
            // Clear the error message
            setError(null);

            // Fetch reservations from the server
            const response = await fetch("https://localhost:8080/getReservations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userID: userID,
                    authToken: authToken,
                })
            });
            const data = await response.json();
            if (data.error) {
                // Display the error message
                setError(data.error);
            } else {
                // Only include the reservations for the selected date
                setReservations(
                    data.reservations.filter(reservation => {
                        const reservationDate = new Date(reservation.datetime);
                        const dateWithoutTime = new Date(reservationDate.getFullYear(), reservationDate.getMonth(), reservationDate.getDate());
                        const selectedDateWithoutTime = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate());
                        
                        // Include this reservation if the reservation is for the selected date
                        return dateWithoutTime.getTime() == selectedDateWithoutTime.getTime();
                    })
                );
            }
        }
        getReservations();
    }, [selectedDate]);

    return (
        <div className="reservationsPane">
            <h2>Reservations</h2>
            {error && <p>{error}</p>}
            <h3>Select a date</h3>
            <input type="date" value={selectedDate.toISOString().split('T')[0]} onChange={d => setSelectedDate(new Date(d.target.value))} />
            <h3>Reservations for {selectedDate.toDateString()}:</h3>
            {reservations.map(reservation => (
                <Reservation reservation={reservation} userID={userID} authToken={authToken} />
            ))}
        </div>
    );
}

function Reservation({ userID, authToken, reservation }) {
    // State variable to store whether the reservation has been cancelled
    const [cancelled, setCancelled] = useState(false);

    async function cancelReservation() {
        // Send a request to the server to cancel the reservation
        const response = await fetch("https://localhost:8080/cancelReservation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                reservationID: reservation.reservationID,
            })
        });
        const data = await response.json();
        if (!data.error) {
            // The reservation was successfully cancelled
            setCancelled(true);
        }
    }

    if (!cancelled) {
        return (
            <div className="reservation">
                <p>Reservation ID: {reservation.reservationID}</p>
                <p>Table number: {reservation.tableID}</p>
                <p>Time: {new Date(reservation.datetime).toLocaleTimeString()}</p>
                <p>Number of people: {reservation.persons}</p>
                <p>Name: {reservation.userName} ({reservation.userEmail})</p>
                <button onClick={cancelReservation}>Cancel reservation</button>
            </div>
        );
    }
}

export default function ViewReservations({ setPage, backPage }) {
    // Check that the user is signed in before allowing them to view the restaurant's reservations
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
            <button className="backButton" onClick={backPage}>Go back</button>
            <ReservationsPane userID={userID} authToken={authToken} />
        </>
    );
}