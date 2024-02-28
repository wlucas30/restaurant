import React, { useState, useEffect } from 'react';
import "./OrderStatus.css";

function StatusPane({ foodOrderID }) {
    // State variable which stores the order status
    const [eta, setEta] = useState("Calculating...");
    const [etaError, setEtaError] = useState(null);

    function fetchEta() {
        // Send a request to the server to get the order's ETA
        fetch("https://localhost:8080/getOrderEta", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                foodOrderID: foodOrderID
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                setEtaError(data.error);
            } else {
                setEta(data.eta);
            }
        });
    }
    fetchEta();

    // Recalculate the order ETA every 30 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            fetchEta();
        }, 30000);
        return () => clearInterval(interval); // Close the timer when the component is unmounted
    }, []);

    return (
        <div className="statusPane">
            <h2>Order Status</h2>
            <p>Your order has been placed and sent to the restaurant!</p>
            <hr />
            <p>Order #{foodOrderID}</p>
            {etaError === null &&
            <p>Estimated time of arrival: {eta}</p>}
            {etaError !== null &&
            <p>Waiting time: {etaError}</p>}
        </div>
    );
}

export default function OrderStatus({ foodOrderID, setPage, backPage }) {
    return ( 
        <>
            <button className="backButton" onClick={() => setPage("home")}>Go home</button>
            <StatusPane foodOrderID={foodOrderID} />
        </>
    );
}