import React, { useState, useEffect } from 'react';
import "./PlaceFoodOrder.css";

// This component displays a list of all the items stored for a restaurant
function RestaurantMenuPane({ order, setOrder, userID, authToken, restaurantID, setPage }) {
    // State variable which stores the restaurant's items
    const [menu, setMenu] = useState([]);
    const [menuError, setMenuError] = useState(null); // stores any error messages returned by the server

    useEffect(() => {
        // This effect is used to fetch the restaurant's menu from the server upon component load
        async function fetchRestaurantMenu() {
            // Send a request to the server to get the restaurant's menu
            const response = await fetch("https://localhost:8080/getMenu", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    restaurantID: restaurantID
                })
            });
            // Decode the response as JSON
            const data = await response.json();
            if (data.error) {
                setMenuError(data.error);
            } else {
                setMenu(data.menu);
            }
        }
        fetchRestaurantMenu();
    }, []);

    // Map the restaurant menu items to a list of ItemOption components
    return (
        <div className="restaurantMenuPane">
            {menuError && <p>{menuError}</p>}
            <h2>Menu</h2>
            <hr />
            {menu.map((item) =>
                <ItemOption
                    item={item} restaurantID={restaurantID} order={order} setOrder={setOrder}
                    userID={userID} authToken={authToken} setPage={setPage}
                />
            )}
        </div>
    );
}

function ItemOption({ item, restaurantID, order, setOrder, userID, authToken, setPage }) {
    // State variable for storing the quantity of the item in the user's current order
    const [quantity, setQuantity] = useState(0);

    // Create an effect so the order is updated when the quantity changes
    useEffect(() => {
        // Find the item in the user's order
        const itemIndex = order.findIndex(orderItem => orderItem.menuItemID === item.menuItemID);
        let newOrder = [...order]; // Create a new copy of the order
        if (itemIndex !== -1) {
            // If the item is already in the order, update the quantity
            newOrder[itemIndex].quantity = quantity;
            newOrder[itemIndex].price = parseFloat(item.price) * quantity;
        } else {
            // If the item is not in the order, add it
            newOrder.push({
                menuItemID: item.menuItemID,
                quantity: quantity,
                price: parseFloat(item.price) * quantity
            });
        }
        setOrder(newOrder); // Set the state to the new copy of the order
    }, [quantity]);

    // This component displays a single item from the restaurant's menu
    return (
        <div className="itemOption">
            <h3>{item.name}</h3>
            {item.image !== null &&
            <img className="menuItemImage"
                src={`data:image/jpeg;base64,${item.image}`}
                alt="Image failed to load" 
            />
            }
            <p>{item.description}</p>
            <p><strong>Price:</strong> £{item.price}</p>
            <p>Calories: {item.calories}kcal</p>

            <div className="quantitySelector">
                <p>Quantity:</p>
                <button onClick={() => setQuantity(quantity + 1)}>+</button>
                <p>{quantity}</p>
                <button onClick={() => setQuantity(Math.max(quantity - 1, 0))}>-</button>
            </div>
            <hr />
        </div>
    );
}

function CurrentOrder({ order, userID, authToken, restaurantID, setPage }) {
    // This component displays the current total price and allows the user to place the order
    const [totalPrice, setTotalPrice] = useState(0);
    const [tableNumber, setTableNumber] = useState(0);
    const [customisation, setCustomisation] = useState(""); // special requests
    const [error, setError] = useState(null);

    // Create an effect to update the total price when the order changes
    useEffect(() => {
        // Calculate the total price of the order
        let newTotalPrice = 0;
        order.forEach(item => {
            newTotalPrice += item.price;
        });
        // Round to 2dp to avoid floating point errors
        setTotalPrice(newTotalPrice.toFixed(2));
    }, [order]);

    async function placeOrder() {
        // Clear errors
        setError(null);

        // Reformat the user's order so that it only includes the menuItemID and quantity
        const formattedOrder = order.map(item => {
            return {
                menuItemID: item.menuItemID,
                quantity: item.quantity
            };
        });
        
        // Send a request to the server to place the user's order
        const response = await fetch("https://localhost:8080/placeOrder", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                restaurantID: restaurantID,
                tableID: parseInt(tableNumber),
                menuItems: formattedOrder,
                customisation: customisation
            })
        });

        // Decode the response as JSON
        const data = await response.json();
        if (data.error != null) {
            setError(data.error);
        } else {
            // The order was successfully placed, so navigate to the order status page
            setPage("orderStatus:" + data.foodOrderID);
        }
    }

    return (
        <div className="currentOrder">
            {error && <p>{error}</p>}
            <h2>Current Order</h2>
            <p>Total Price: £{totalPrice}</p>
            <input type="number" placeholder="Table number" onChange={n => setTableNumber(n.target.value)} />
            <button onClick={placeOrder}>Place Order</button>
            <input type="text" placeholder="Customisation requests" onChange={c => setCustomisation(c.target.value)}
            className="customisation" />
        </div>
    );
}

export default function PlaceFoodOrder({ restaurantID, setPage, backPage }) {
    // Check that the user is signed in before allowing them to place a food order
    let userID, authToken;
    try {
        userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
        authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];
    } catch {
        // If the cookies are not present, the user is not signed in
        setPage("signIn");
    }

    // State variable for storing the user's current order
    const [order, setOrder] = useState([]);

    return (
        <>
            <button className="backButton" onClick={backPage}>Go back</button>
            <CurrentOrder order={order} userID={userID} authToken={authToken} restaurantID={restaurantID} setPage={setPage} />
            <RestaurantMenuPane order={order} setOrder={setOrder} userID={userID} authToken={authToken}
            restaurantID={restaurantID} setPage={setPage} />
        </>
    );
}