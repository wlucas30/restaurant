import React, { useState, useEffect } from 'react';
import "./ChangeEmail.css";

function ChangeEmailForm({ setPage }) {
    const [emailChangeError, setEmailChangeError] = useState(null);
    const [email, setEmail] = useState(""); 
    const [confirmEmail, setConfirmEmail] = useState("");

    async function changeEmail() {
        setEmailChangeError(null); // Reset the error message

        // Check that the emails match
        if (email != confirmEmail) {
            setEmailChangeError("Emails do not match");
        }

        // Validate the email using a regular expression before sending it to the backend
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setEmailChangeError("Invalid email address");
            return;
        }

        // The email is assumed to be valid, so retrieve stored cookies for authentication
        const userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
        const authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];

        // Send the new email to the backend
        const response = await fetch('https://localhost:8080/changeEmail', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                newEmail: email
            })
        })

        // Decode the response as JSON
        const data = await response.json();

        // Check for errors
        if (data.error) {
            // Set the error message
            setEmailChangeError(data.error);
        } else {
            // The request succeeded, so sign the user out
            document.cookie = "userID=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            document.cookie = "authToken=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
            setPage("home");
        }
    }

    return (
        <div className="changeEmailForm">
            <h2>Enter your new email below</h2>
            <p>Warning: Ensure that the new email address is correct. Upon submitting, you will be signed out.</p>
            {emailChangeError != null && <p>{emailChangeError}</p>}
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="email" placeholder="Confirm email" value={confirmEmail} onChange={(e) => setConfirmEmail(e.target.value)} />
            <button onClick={changeEmail}>Confirm</button>
        </div>
    );
}

export default function ChangeEmail({ setPage, backPage }) {
    return (
        <>
            <button className="backButton" onClick={backPage}>Back</button>
            <ChangeEmailForm setPage={setPage} />
        </>
    );
}