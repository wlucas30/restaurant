import React, { useState, useEffect } from 'react';
import "./ManageMenu.css";

function MenuManagementPane({ userID, authToken, restaurantID }) { 
    // State variable for storing the restaurant's existing menu
    const [menu, setMenu] = useState([]);
    const [menuError, setMenuError] = useState(null);
    const[tempMenu, setTempMenu] = useState(null); // used for triggering a refresh of the menu

    // Effect which retrieves the restaurant's menu once the restaurantID
    useEffect(() => {
        async function fetchMenu() {
            const response = await fetch("https://localhost:8080/getMenu", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    restaurantID: restaurantID
                })
            });
            const data = await response.json();
            if (data.error) {
                setMenuError(data.error);
            } else {
                setMenu(data.menu);
            }
        }
        fetchMenu();
    }, [restaurantID, tempMenu]);

    return (
        <div className="menuManagementPane">
            <h2>Menu Management</h2>
            <hr />
            {menuError && <p>{menuError}</p>}
            <h3>Current Menu</h3>
            {menu.map((item) =>
                <MenuItem item={item} restaurantID={restaurantID} userID={userID} authToken={authToken} />
            )}<hr />
            <NewItemContainer restaurantID={restaurantID} userID={userID} authToken={authToken} 
            setTempMenu={setTempMenu} />
        </div>
    );
}

function NewItemContainer({ restaurantID, userID, authToken, setTempMenu }) {
    // State variables for storing the details of the new item
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [price, setPrice] = useState("");
    const [calories, setCalories] = useState("");
    const [section, setSection] = useState("");
    const [message, setMessage] = useState(null);

    async function createNewItem() {
        // Reset the message
        setMessage(null);

        // Make a request to the server to create the new item
        const response = await fetch("https://localhost:8080/addMenuItem", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                restaurantID: restaurantID,
                name: name,
                description: description,
                price: parseFloat(price),
                calories: parseInt(calories),
                menuSection: section,
                changeExistingID: null // This is a new item, so not needed here
            })
        });
        const data = await response.json();
        if (data.error) {
            setMessage("An error occurred creating the new item: " + data.error);
        } else {
            setMessage("New item created successfully");
            // Reset the form
            setName("");
            setDescription("");
            setPrice("");
            setCalories("");
            setSection("");

            // Trigger a refresh of the menu by setting the menu state variable to a dummy value
            setTempMenu(["refresh"]);
        }
    }

    return (
        <div className="menuItem">
            <h3>Create a new item</h3>
            {message && <p>{message}</p>}
            <input type="text" value={name} onChange={(n) => setName(n.target.value)} 
            placeholder="Item name" /><br />
            <textarea type="text" value={description} onChange={(d) => setDescription(d.target.value)}
            placeholder="Item description" /><br />
            <label for="price">£</label>
            <input type="decimal" value={price} onChange={(p) => setPrice(p.target.value)} 
            placeholder="Item price (£)" name="price" /><br />
            <input type="number" value={calories} onChange={(c) => setCalories(c.target.value)}
            name="calories" placeholder="Calories" />
            <label for="calories">kcal</label><br />
            <input type="text" value={section} onChange={(s) => setSection(s.target.value)}
            placeholder="Item section" /><br />
            <button onClick={createNewItem}>Submit new item</button>
        </div>
    );
}

function MenuItem({ item, userID, authToken }) {
    // State variables for storing item details
    const [name, setName] = useState(item.name);
    const [description, setDescription] = useState(item.description);
    const [price, setPrice] = useState(item.price);
    const [calories, setCalories] = useState(item.calories);
    const [section, setSection] = useState(item.section);
    const [message, setMessage] = useState(null);
    const [deleted, setDeleted] = useState(false);
    
    // Effect to initialise the state variables when an item is provided
    useEffect(() => {
        console.log(item);
        setName(item.name);
        setDescription(item.description);
        setPrice(item.price);
        setCalories(item.calories);
        setSection(item.section);
    }, [item]);

    // State variable for storing the image to be uploaded
    const [imageFile, setImageFile] = useState(null);

    async function saveChanges() {
        // Reset the message
        setMessage(null);

        // Make a request to the server to update the item
        const response = await fetch("https://localhost:8080/addMenuItem", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                changeExistingID: item.menuItemID,
                name: name,
                description: description,
                price: parseFloat(price),
                calories: parseInt(calories),
                menuSection: section
            })
        });
        const data = await response.json();
        if (data.error) {
            setMessage("An error occurred updating the details: " + data.error);
        } else {
            setMessage("Details updated successfully");
        }
    }

    async function uploadImage() {
        // Reset the message
        setMessage(null);

        // Check that an image has been selected
        if (!imageFile) {
            setMessage("No image selected");
            return;
        }

        // Send a request to the server to upload the new image
        const formData = new FormData();
        formData.append("data", JSON.stringify({
            userID: userID,
            authToken: authToken,
            menuItemID: item.menuItemID
        }));
        formData.append("image", imageFile);
        const response = await fetch("https://localhost:8080/uploadMenuItemImage", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (data.error) {
            setMessage("An error occurred uploading the image: " + data.error);
        } else {
            setMessage("Image uploaded successfully!");
        }
    }

    async function deleteItem() {
        // Reset the message
        setMessage(null);

        // Send a request to the server to delete the item
        const response = await fetch("https://localhost:8080/deleteMenuItem", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userID: userID,
                authToken: authToken,
                menuItemID: item.menuItemID
            })
        });
        const data = await response.json();
        if (data.error) {
            setMessage("An error occurred deleting the item: " + data.error);
        } else {
            setDeleted(true);
        }
    }

    if (!deleted) {
        return (
            <div className="menuItem">
                {message && <p>{message}</p>}
                <input type="text" value={name} onChange={(n) => setName(n.target.value)} 
                placeholder="Item name" /><br />
                {item.image !== null &&
                <img className="menuItemImage" src={`data:image/jpeg;base64,${item.image}`} />}
                <textarea type="text" value={description} onChange={(d) => setDescription(d.target.value)}
                placeholder="Item description" /><br />
                <label for="price">£</label>
                <input type="decimal" value={price} onChange={(p) => setPrice(p.target.value)} 
                placeholder="Item price (£)" name="price" /><br />
                <input type="number" value={calories} onChange={(c) => setCalories(c.target.value)}
                name="calories" placeholder="Calories" />
                <label for="calories">kcal</label><br />
                <input type="text" value={section} onChange={(s) => setSection(s.target.value)}
                placeholder="Item section" /><br />
                <input type="file" onChange={(f) => setImageFile(f.target.files[0])} /><br />
                {item.image === null && <button onClick={uploadImage}>Upload image</button>}<br />
                <button onClick={saveChanges}>Save changes</button>
                <button onClick={deleteItem}>Delete item</button>
            </div>
        );
    }
}

export default function ManageMenu({ setPage, backPage }) {
    // Check that the user is signed in before allowing them to manage their menu
    let userID, authToken;
    try {
        userID = parseInt(document.cookie.split('; ').find(row => row.startsWith('userID=')).split('=')[1]);
        authToken = document.cookie.split('; ').find(row => row.startsWith('authToken=')).split('=')[1];
    } catch {
        // If the cookies are not present, the user is not signed in
        setPage("signIn");
    }

    // Fetch the user's restaurantID on component load
    const [restaurantID, setRestaurantID] = useState(null);
    useEffect(() => {
        async function getRestaurantID() {
            const response = await fetch("https://localhost:8080/getRestaurantID", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    userID: userID,
                })
            })
            const data = await response.json();
            if (data.error) {
                // The user does not have a restaurant, so they cannot access this page
                backPage();
            } else {
                setRestaurantID(data.restaurantID);
            }
        }
        getRestaurantID()
    }, []);

    return (
        <>
            <button className="backButton" onClick={backPage}>Go back</button>
            <MenuManagementPane userID={userID} authToken={authToken} restaurantID={restaurantID} />
        </>
    );
}