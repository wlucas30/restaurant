import React, { useState, useEffect } from 'react';
import "./SignIn.css";

function SignInForm({ setPage }) {
    // State variables for the sign-in form
    const [email, setEmail] = useState("");
    const [name, setName] = useState("");
    const [signInError, setSignInError] = useState(null);

    // Stores whether the user is signing in or creating an account
    const [signInOption, setSignInOption] = useState("true");

    // Function to handle the sign-in form submission
    async function beginVerification() {
        // Reset any stored errors from previous attempts
        setSignInError(null);

        // Validate the email using a regular expression before sending it to the backend
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setSignInError("Invalid email address");
            return;
        }

        // Make a request with the email and name
        var body = null;
        if (signInOption === "true") {
            // The name should be included
            body = JSON.stringify({
                email: email,
                name: name
            });
        } else {
            // The name should be sent as null
            body = JSON.stringify({
                email: email,
                name: null
            });
        }
        
        const response = await fetch('https://localhost:8080/beginVerification', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: body
		});

		// Decode the response as JSON
		const data = await response.json();

		// Check for errors
		if (data.error) {
			// Set the error message
            setSignInError(data.error);
		} else {
			// The request succeeded, so move on to the code verification page
            // Retrieve the userID of the account which is being signed in to or created
            const userID = data.userID;
            setPage("verifyCode:" + userID);
		}
    }
    
    return (
        <div className="signInForm">
            <h2>Sign in or create an account</h2>
            {signInError != null && <p>{signInError}</p>}
            {signInOption === "true" && <input type="text" value={name} onChange={(n) => setName(n.target.value)} placeholder="Name" />}
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />

            {signInOption === "true" && <button onClick={beginVerification}>Sign up</button>}
            {signInOption === "false" && <button onClick={beginVerification}>Sign in</button>}

            <hr /><div className="radioForm">
                <input checked={signInOption === "false"} type="radio" id="signIn" name="signInOption" value="false"
                onChange={(option) => setSignInOption(option.target.value)}
                />
                <label for="signIn">Sign In</label><br />
                <input checked={signInOption === "true"} type="radio" id="signUp" name="signInOption" value="true"
                onChange={(option) => setSignInOption(option.target.value)}
                />
                <label for="signUp">Create an account</label>
            </div>
        </div>
    );
}

export default function SignIn({ setPage, backPage }) {
    // Retrieve cookies to check if the user is already signed in
    useEffect(() => {
        const cookies = document.cookie.split('; ');
        const authTokenCookie = cookies.find(cookie => cookie.startsWith('authToken='));

        if (authTokenCookie) {
            // We assume that the user is signed in if an authentication token is present
            setPage("accountDetails");
        }
    }, []);

    return (
        <>
            <button className="backButton" onClick={() => backPage()}>Back</button>
            <SignInForm setPage={setPage} />
        </>
    );
}