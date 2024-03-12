import React, { useState, useEffect } from 'react';
import "./ManageTables.css";

function TableManagementPane({ userID, authToken, setPage }) {
    // State variables for storing all of the restaurant's tables
    const [tables, setTables] = useState([]);
    const [error, setError] = useState(null);

    // Retrieve the restaurant's tables from the backend
    useEffect(() => {
        async function getTables() {
            const response = await fetch("https://localhost:8080/retrieveTables", {
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
                setError(data.error);
            } else {
                setTables(data.tables);
            }
        }
        getTables();
    }, []);

    return (
        <div className="tableManagementPane">
            <h2>Manage Tables</h2>
            {error && <p>{error}</p>}
            <h3>Existing tables</h3>
            {tables.map(table => (
                <RestaurantTable table={table} userID={userID} authToken={authToken} setPage={setPage} />
            ))}
            <hr /><h3>Create a new table</h3>
            <CreateNewTable userID={userID} authToken={authToken} tables={tables} setTables={setTables} />
        </div>
    );
}

function CreateNewTable({ userID, authToken, tables, setTables }) {
    // Initialise state variables for storing the new table's details
    const [tableNumber, setTableNumber] = useState("");
    const [capacity, setCapacity] = useState("2");
    const [message, setMessage] = useState(null);

    async function createNew() {
        // Upload the inputted details to the server
        const response = await fetch("https://localhost:8080/createTable", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                tableNumber: parseInt(tableNumber),
                capacity: parseInt(capacity),
            })
        });
        const data = await response.json();
        if (data.error) {
            setMessage(data.error);
        } else {
            setMessage("Table created successfully");
            // Add the new table to the list of tables to be displayed
            const tempTables = structuredClone(tables);
            tempTables.push({
                tableID: data.tableID,
                tableNumber: parseInt(tableNumber),
                capacity: parseInt(capacity),
            });
            setTables(tempTables);
        }
    }

    return (
        <div className="tableContainer">
            {message && <p>{message}</p>}
            <label for="tableNumber">Table number:</label>
            <input type="number" name="tableNumber" value={tableNumber} 
            onChange={(n) => setTableNumber(n.target.value)} />

            <label for="capacity">Capacity:</label>
            <input type="number" name="capacity" value={capacity}
            onChange={(c) => setCapacity(c.target.value)} />

            <button onClick={createNew}>Create new table</button>
        </div>
    );
}

function RestaurantTable({ table, userID, authToken, setPage }) {
    const [tableNumber, setTableNumber] = useState(null);
    const [capacity, setCapacity] = useState(null);
    const [message, setMessage] = useState(null);
    const [deleted, setDeleted] = useState(false);

    // Effect which creates state variables for all of the table's data
    useEffect(() => {
        setTableNumber(table.tableNumber);
        setCapacity(table.capacity);
    }, []);

    async function submitChanges() {
        // Send the updated table details to the backend
        const response = await fetch("https://localhost:8080/editTable", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                tableID: table.tableID,
                tableNumber: parseInt(tableNumber),
                capacity: parseInt(capacity),
            })
        });
        const data = await response.json();
        if (data.error) {
            setMessage(data.error);
        } else {
            setMessage("Table details updated successfully");
        }
    }

    async function deleteTable() {
        // Send the table's ID to the backend to be deleted
        const response = await fetch("https://localhost:8080/deleteTable", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                tableID: table.tableID,
            })
        });
        const data = await response.json();
        if (data.error) {
            setMessage(data.error);
        } else {
            // This removes the table from the displayed list of tables
            setDeleted(true);
        }
    }

    if (!deleted) {
        return (
            <div className="tableContainer">
                {message && <p>{message}</p>}
                <label for="tableNumber">Table number:</label>
                <input type="number" name="tableNumber" value={tableNumber} 
                onChange={(n) => setTableNumber(n.target.value)} />

                <label for="capacity">Capacity:</label>
                <input type="number" name="capacity" value={capacity}
                onChange={(c) => setCapacity(c.target.value)} />

                <button onClick={() => setPage("viewTableBill:" + table.tableNumber)}>View bill</button>
                <button onClick={submitChanges}>Submit table changes</button>
                <button onClick={deleteTable}>Delete table</button>
            </div>
        );
    }
}

export default function ManageTables({ setPage, backPage }) {
    // Check that the user is signed in before allowing them to manage their tables
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
            <TableManagementPane userID={userID} authToken={authToken} setPage={setPage} />
        </>
    );
}