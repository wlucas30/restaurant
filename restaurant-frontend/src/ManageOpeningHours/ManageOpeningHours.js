import React, { useState, useEffect } from 'react';
import "./ManageOpeningHours.css";

function OpeningHoursPane({ userID, authToken }) {
    // State variables for the opening hours
    const [openingHours, setOpeningHours] = useState({});
    const [openingHoursError, setOpeningHoursError] = useState(null);

    async function updateOpeningHours() {
        // Clear any previous errors
        setOpeningHoursError(null);

        // Send a request to the server to update the opening hours
        const response = await fetch("https://localhost:8080/setOpeningPeriods", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                openingPeriods: openingHours
            })
        });
        const data = await response.json();
        if (data.error) {
            setOpeningHoursError(data.error);
        }
    }

    // List of days for mapping each day to a separate component
    let days = [{dayName: "Monday", dayNumber: 1}, {dayName: "Tuesday", dayNumber: 2},
    {dayName: "Wednesday", dayNumber: 3}, {dayName: "Thursday", dayNumber: 4}, {dayName: "Friday", dayNumber: 5}, 
    {dayName: "Saturday", dayNumber: 6}, {dayName: "Sunday", dayNumber: 7}];

    return (
        <div className="openingHoursPane">
            <h2>Manage opening hours</h2>
            <p>Warning: By changing opening hours, any reservations which are placed for a time 
                which is now invalid will be automatically cancelled.</p>
            {openingHoursError && <p>{openingHoursError}</p>}
            {days.map(day => <OpeningHoursDay dayName={day.dayName} dayNumber={day.dayNumber} 
            openingHours={openingHours} setOpeningHours={setOpeningHours} />)}
            <button onClick={updateOpeningHours}>Set opening hours</button>
        </div>
    );
}

function OpeningHoursDay({ dayName, dayNumber, openingHours, setOpeningHours }) {
    // State variable and function for enabling and disabling the input fields (for closed days)
    const [isEnabled, setIsEnabled] = useState(true);
    function toggleEnabled() {
        const newIsEnabled = !isEnabled;
        setIsEnabled(!isEnabled);
        if (!newIsEnabled) {
            // Remove the opening hours from the openingHours state variable
            try {
                let newOpeningHours = structuredClone(openingHours);
                delete newOpeningHours[dayNumber.toString()];
                setOpeningHours(newOpeningHours);
            } catch {
                // If no record exists, do nothing
            }
        } else {
            // Reinput the entered opening hours
            updateLocallyStoredOpeningHours();
        }
    };

    function updateLocallyStoredOpeningHours() {
        // Get the opening and closing times from the input fields
        const openTimeString = document.getElementById(`${dayName}Open`).value.toString();
        const closeTimeString = document.getElementById(`${dayName}Close`).value.toString();
        const dayNumberString = dayNumber.toString();

        // Create a new openingHours dictionary with the updated opening hours
        let newOpeningHours = structuredClone(openingHours);
        newOpeningHours[dayNumberString] = {openingTime: openTimeString, closingTime: closeTimeString};

        // Update the openingHours state variable
        setOpeningHours(newOpeningHours);
    }
    return (
        <div className="openingHoursDay">
            <h3>{dayName}</h3>
            <label htmlFor={`${dayName}Enabled`}>Open on this day?</label>
            <input type="checkbox" id={`${dayName}Enabled`} name={`${dayName}Enabled`} checked={isEnabled} onChange={toggleEnabled} />
            <label htmlFor={`${dayName}Open`}>Open:</label>
            <input type="time" id={`${dayName}Open`} name={`${dayName}Open`} disabled={!isEnabled} onChange={updateLocallyStoredOpeningHours}/>
            <label htmlFor={`${dayName}Close`}>Close:</label>
            <input type="time" id={`${dayName}Close`} name={`${dayName}Close`} disabled={!isEnabled} onChange={updateLocallyStoredOpeningHours}/>
        </div>
    );
}

export default function ManageOpeningHours({ setPage, backPage }) {
    // Check that the user is signed in before rendering the page
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
            <OpeningHoursPane userID={userID} authToken={authToken} />
        </>
    );    
}