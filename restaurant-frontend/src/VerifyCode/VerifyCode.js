import React, { useState, useEffect } from 'react';
import "./VerifyCode.css";

function CodeVerificationForm({ userID, setPage }) {
    // State variables for the sign-in form
    const [code, setCode] = useState("");
    const [error, setError] = useState(null);

    // Function which sends the code to the backend for verification
    async function verifyCode() {
        // Reset the error message
        setError(null);

        // Check that the code is a 6-digit number
        const codeRegex = /^[0-9]{6}$/;
        if (!codeRegex.test(code)) {
            setError("Invalid code");
            return;
        }

        // Request an authentication token from the backend using the provided code
        const response = await fetch('https://localhost:8080/getAuthToken', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userID: userID,
                code: code
            })
        });

        // Decode the response as JSON
        const data = await response.json();

        // Check for errors
        if (data.error) {
            // Set the error message
            setError(data.error);
            return;
        }

        // The request succeeded, so fetch the plaintext authentication token from the response
        const authToken = data.authToken;

        // Calculate the expiry date of the authentication cookie (7 days from now)
        let date = new Date();
        date.setDate(date.getDate() + 7);

        // Store the authentication token in a cookie
        document.cookie = "authToken=" + authToken + "; Secure; SameSite=Strict; expires=" + date.toUTCString();

        // Move on to the home page
        setPage("home");
    }

    return (
        <div className="codeForm">
            <h2>We've emailed you 📧</h2>
            <p>We sent you a code. Check your inbox and type in the code below.</p><hr />
            {error != null && <p>{error}</p>}
            <input type="number" inputMode="numeric" 
            placeholder="Verification code" value={code} onChange={(c) => setCode(c.target.value)} />
            <button onClick={verifyCode}>Submit code</button>
        </div>
    );
}

export default function VerifyCode({ userID, setPage, backPage }) {
    return (
        <>
            <button className="backButton" onClick={() => backPage()}>Back</button>
            <CodeVerificationForm userID={userID} setPage={setPage} />
        </>
    );
}