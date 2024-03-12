import React, { useState, useEffect } from 'react';
import "./ViewTableBill.css";

function UnpaidOrdersPane({ userID, authToken, tableID }) {
    // State variable for storing unpaid orders
    const [unpaidOrders, setUnpaidOrders] = useState([]);
    const [error, setError] = useState(null);

    // Retrieve the table's unpaid orders from the backend
    useEffect(() => {
        async function getUnpaidOrders() {
            const response = await fetch("https://localhost:8080/getTableBill", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    tableID: tableID,
                })
            });
            const data = await response.json();
            if (data.error) {
                setError(data.error);
            } else {
                setUnpaidOrders(data.orders);
            }
        }
        getUnpaidOrders();
    }, []);

    return (
        <div className="unpaidOrdersPane">
            <h2>Unpaid Orders</h2>
            {error && <p>{error}</p>}
            {unpaidOrders.map(order => (
                <UnpaidOrder order={order} userID={userID} authToken={authToken} />
            ))}
        </div>
    );
}

function UnpaidOrder({ order, userID, authToken }) {
    // Variable which determines whether the order should be displayed
    const [paid, setPaid] = useState(false);

    async function markAsPaid() {
        // Send the orderID to the backend to mark it as paid
        const response = await fetch("https://localhost:8080/orderConfirmation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                foodOrderID: order.foodOrderID,
                confirmed: null, // not used for this request
                fulfilled: null, // not used for this request
                paid: true
            })
        });
        const data = await response.json();
        if (!data.error) {
            // If the request is successful, update the order's status
            setPaid(true);
        }
    }

    if (!paid) {
        return (
            <div className="unpaidOrder">
                <p>Order ID: {order.foodOrderID}</p>
                <p>Order total: £{order.price}</p>
                <p><strong>Order items:</strong></p>
                <p>{order.menuItems}</p>
                <p><strong>Time ordered:</strong> {order.timeOrdered}</p> 
                <button onClick={markAsPaid}>Mark as paid</button>
            </div>
        );
    }
}

export default function ViewTableBill({ tableID, setPage, backPage }) {
    // Check that the user is signed in before allowing them to view the table's bills
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
            <UnpaidOrdersPane userID={userID} authToken={authToken} tableID={tableID} />
        </>
    );
}