import React, { useState, useEffect } from 'react';
import "./OrderQueue.css";

function OrderQueuePane({ userID, authToken }) {
    // This method is used to create a new node for the queue linked list
    function createQueueNode(order, next) {
        return { order: order, next: next }; // returns the node as an object
    }

    // The queue is stored as a linked list - this is the head
    const [queueHead, setQueueHead] = useState(createQueueNode(null, null));
    const [queueError, setQueueError] = useState(null);

    var currentOrderID = 0; // ID of most recent order loaded
    
    // This method adds a new order to the back of the queue
    function enqueueOrder(order) {
        // Check the orderID to ensure it is not already in the queue
        if (order.foodOrderID <= currentOrderID) {
            return; // do nothing
        }
        let current = queueHead;
        while (current.next !== null) { // iterate until the end of the queue is reached
            current = current.next;
        }
        current.next = createQueueNode(order, null);
        // Update the queueHead state variable to trigger a re-render
        setQueueHead(structuredClone(queueHead));
    }

    // This method removes an order from the queue by ID
    function dequeueOrder(foodOrderID) {
        let current = queueHead;
        while (current.next !== null) { // iterate until the end of the queue is reached
            if (current.next.order.foodOrderID === foodOrderID) {
                current.next = current.next.next; // removes reference to the order
                return;
            }
            current = current.next;
        }
        // Update the queueHead state variable to trigger a re-render
        setQueueHead(structuredClone(queueHead));
    }

    // orders are loaded lazily to avoid repeatedly loading the entire queue at once
    async function fetchOrderQueue() {
        // Clear the error message
        setQueueError(null);

        // This function is called repeatedly to fetch the order queue
        const response = await fetch("https://localhost:8080/getOrderQueue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                lastStoredFoodOrderID: currentOrderID
            })
        })
        await response.json()
        .then(data => {
            if (data.error) {
                setQueueError(data.error);
            } else {
                // Append the new orders to the queue
                for (let order of data.orders) {
                    enqueueOrder(order);
                }
                // Update the current order ID
                try {
                    currentOrderID = data.orders[data.orders.length - 1].foodOrderID;
                } catch {
                    // An exception could occur if the queue is empty - in this case do nothing
                }
            }
        });
    }

    // Fetch the order queue every 10 seconds
    useEffect(() => {
        fetchOrderQueue();
        const interval = setInterval(() => {
            fetchOrderQueue();
        }, 10000);
        return () => clearInterval(interval); // Close the timer when the component is unmounted
    }, []);

    // Reformat the order queue as a list of Order components
    let orderItems = [];
    let currentNode = queueHead;
    while (currentNode !== null) {
        if (currentNode.order !== null) {
            orderItems.push(<Order order={currentNode.order} dequeueOrder={dequeueOrder} userID={userID} authToken={authToken} />);
        }
        currentNode = currentNode.next;
    }

    return (
        <div className="orderQueuePane">
            {queueError && <p>{queueError}</p>}
            <h2>Order Queue</h2>
            <hr />
            {orderItems}
        </div>
    );
}

function Order({ order, dequeueOrder, userID, authToken }) {
    // State variable for storing the order's status
    const [status, setStatus] = useState("Waiting...");
    const [error, setError] = useState(null);

    // Fetch the order's status on component load
    useEffect(() => {
        if (status != "Removed") { // if the order has been removed, do not check its status
            if (order.confirmed) {
                setStatus("Confirmed"); 
            } else {
                setStatus("Pending");
            }
        }
    });

    async function changeStatus(newStatus) {
        // Send a request to the server to change the order's status
        const response = await fetch("https://localhost:8080/orderConfirmation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                foodOrderID: order.foodOrderID,
                confirmed: newStatus === "confirm" ? true : (newStatus === "reject" ? false : null),
                fulfilled: newStatus === "fulfilled" ? true : null, 
                paid: null // not used in this context, but required by the server
            })
        });
        const data = await response.json();
        if (data.error) {
            setError(data.error);
        }

        // If the status change is successful, remove from queue if rejected or fulfilled
        if (error === null && (newStatus === "fulfilled" || newStatus === "reject")) {
            // Remove the order from the queue
            dequeueOrder(order.foodOrderID);
            setStatus("Removed");
        }
        if (error === null && newStatus === "confirm") {
            setStatus("Confirmed");
            order.confirmed = true;
        }
    }

    if (status != "Removed") {
        return (
            <div className="orderElement">
                {error && <p>{error}</p>}
                <p>Order ID: {order.foodOrderID}</p>
                <p>Table number: {order.tableID}</p>
                <p>Status: {status}</p>
                <p>Contents:</p>
                <ul>{
                    order.orderItems.map(item => {
                        return <li>{item.name}</li>
                    })
                }</ul>
                {!order.confirmed && <div className="orderOptions">
                    <button onClick={() => changeStatus("confirm")}>Confirm</button>
                    <button onClick={() => changeStatus("reject")}>Reject</button>
                </div>}
                {order.confirmed && <div className="orderOptions">
                    <button onClick={() => changeStatus("fulfilled")}>Mark as fulfilled</button>
                </div>}
            </div>
        );
    }
}

export default function OrderQueue({ setPage, backPage }) {
    // Check that the user is signed in before displaying the order queue
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
            <OrderQueuePane userID={userID} authToken={authToken} />
        </>
    );
}