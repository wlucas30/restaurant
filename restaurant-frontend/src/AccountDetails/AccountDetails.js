import React, { useState, useEffect } from 'react';
import "./AccountDetails.css";

function AccountInformationPane({ setPage }) {
    // State variables for storing account information
    const [email, setEmail] = useState(null);
    const [name, setName] = useState(null);
    const [professional, setProfessional] = useState(false);

    // Retrieve the account userID and authentication token from cookies
    let userID, authToken;
    try {
        userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
        authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];
    } catch {
        // If the cookies are not present, the user is not signed in
        setPage("signIn");
    }

    // Retrieve the account information from the backend
    useEffect(() => {
        async function retrieveAccountInformation() {
            // Make a POST request to the backend to retrieve account information
            const response = await fetch("https://localhost:8080/accountDetails", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userID: userID,
                    authToken: authToken
                })
            });

            // Decode the response as JSON
            const data = await response.json();

            // Check for errors
            if (data.error) {
                // If an error occurred, the user cannot be authenticated, so delete their cookies
                document.cookie = "userID=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
                document.cookie = "authToken=; expires=Thu, 01 Jan 1970 00:00:00 GMT";

                // Move to the sign-in page
                setPage("signIn");
            } else {
                // Return the account information to be stored in the state variables
                return data;
            }
        }
        retrieveAccountInformation()
            .then((data) => {
                setEmail(data.details.email);
                setName(data.details.name);
                setProfessional(data.details.professional);
            })
    }, [professional]); // updates when user becomes a professional to show the restaurant control panel button

    return (
        <>
            <div className="accountInformationPane">
                <h2>Account Information</h2>
                <h3>Hello! This is your account information:</h3>
                <p><strong>Account name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
            </div>
            <hr />
            <AccountOptionsPane setPage={setPage} professional={professional} setProfessional={setProfessional} />
        </>
    );
}

function AccountOptionsPane({ setPage, professional, setProfessional }) {
    function signOut() {
        // Delete the stored cookies
        document.cookie = "userID=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        document.cookie = "authToken=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    
        // Redirect to the home page
        setPage("home");
    }

    function becomeProfessional() {
        // This promotes the user to professional and creates a new restaurant
        fetch("https://localhost:8080/createRestaurant", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userID: parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]),
                authToken: document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1]
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
            } else {
                setProfessional(true);
            }
        });
    }

    return (
        <div className="accountOptionsPane">
            <h2>Account Options</h2>
            <button onClick={() => setPage("changeEmail")}>Change email address</button>
            {professional === false && <button onClick={becomeProfessional}>Create a new restaurant</button>}
            {professional === true && <button onClick={() => setPage("restaurantControlPanel")}>Restaurant control panel</button>}
            <button onClick={signOut}>Sign out</button>
        </div>
    );
}

export default function AccountDetails({ setPage }) {
    return (
        <>
            <button className="backButton" onClick={() => setPage("home")}>Go home</button>
            <AccountInformationPane setPage={setPage} />
        </>
    );
}