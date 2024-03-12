import React, { useState, useEffect } from 'react';
import "./ControlPanel.css";

function ControlPanelOptions({ setPage, backPage, userID, authToken }) {
    // Retrieve the user's restaurantID from the backend
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

    // This function displays all of the page options for the control panel
    return (
        <div className="controlPanelOptions">
            <h2>Control Panel</h2>
            <p>Restaurant ID: {restaurantID}</p>
            <button onClick={() => setPage("changeRestaurantDetails")}>Change restaurant details</button>
            <button onClick={() => setPage("manageRestaurantImages")}>Manage restaurant images</button>
            <button onClick={() => setPage("manageOpeningHours")}>Manage opening hours</button>
            <button onClick={() => setPage("manageMenu")}>Manage menu</button>
            <button onClick={() => setPage("orderQueue")}>View order queue</button>
            <button onClick={() => setPage("manageTables")}>Manage tables</button>
            <button onClick={() => setPage("viewReservations")}>View reservations</button>
        </div>
    );
}

export default function ControlPanel({ setPage, backPage }) {
    // Check that the user is signed in before displaying the control panel
    let userID, authToken;
    try {
        userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
        authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];
    } catch {
        // If the cookies are not present, the user is not signed in
        backPage();
    }

    return (
        <>
            <button className="backButton" onClick={backPage}>Go back</button>
            <ControlPanelOptions setPage={setPage} userID={userID} authToken={authToken} />
        </>
    );
}