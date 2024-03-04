import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Home from './Home/Home';
import RestaurantPreview from './RestaurantPreview/RestaurantPreview';
import SignIn from './SignIn/SignIn';
import VerifyCode from './VerifyCode/VerifyCode';
import AccountDetails from './AccountDetails/AccountDetails';
import ChangeEmail from './ChangeEmail/ChangeEmail';
import TopBar from './Topbar/Topbar';
import PlaceReview from './PlaceReview/PlaceReview';
import PlaceReservation from './PlaceReservation/PlaceReservation';
import PlaceFoodOrder from './PlaceFoodOrder/PlaceFoodOrder';
import OrderStatus from './OrderStatus/OrderStatus';
import RestaurantControlPanel from './ControlPanel/ControlPanel';
import OrderQueue from './OrderQueue/OrderQueue';

function App() {
	// Initialise a state variable which determines the currently displayed page
	const [page, navigateToPage] = useState("home"); // default page is the home page
	// This stack is used for storing the page history so that the back button can be implemented
	const [pageStack, setPageStack] = useState(["home"]);

	function setPage(newPage) {
		// Push to the page stack
		setPageStack(oldStack => [...oldStack, newPage]);
		// Set the new page
		navigateToPage(newPage);
	}

	function backPage() {
		// Store the new stack temporarily with the front page removed
		const newStack = pageStack.slice(0, -1);
		// Get the new page from the new stack (the page which was open before the current page)
		const newPage = newStack[newStack.length - 1];

		// Update the page stack
		setPageStack(newStack);
		// Navigate to the new page
		navigateToPage(newPage);
	}

	// This function evaluates the current value of the page state variable and returns the appropriate page component
	function renderCurrentPage(currentPage) {
		if (currentPage == "home") {
			return <Home setPage={setPage}/>;
		} else if (currentPage.startsWith("viewRestaurantDetails:")) {
			// Extract restaurantID from the page name and pass it to the RestaurantDetails component
			const restaurantID = parseInt(currentPage.substring("viewRestaurantDetails:".length));
			return <RestaurantPreview restaurantID={restaurantID} setPage={setPage} backPage={backPage}/>;
		} else if (currentPage == "signIn") {
			return <SignIn setPage={setPage} backPage={backPage}/>;
		} else if (currentPage.startsWith("verifyCode:")) {
			// Extract the userID from the page name and pass it to the VerifyCode component
			const userID = parseInt(currentPage.substring("verifyCode:".length));
			return <VerifyCode userID={userID} setPage={setPage} backPage={backPage}/>;
		} else if (currentPage == "accountDetails") {
			return <AccountDetails setPage={setPage} backPage={backPage}/>;
		} else if (currentPage == "changeEmail") {
			return <ChangeEmail setPage={setPage} backPage={backPage}/>;
		} else if (currentPage.startsWith("placeReview:")) {
			// Extract restaurantID from the page name and pass it to the PlaceReview component
			const restaurantID = parseInt(currentPage.substring("placeReview:".length));
			return <PlaceReview restaurantID={restaurantID} setPage={setPage} backPage={backPage}/>;
		} else if (currentPage.startsWith("placeReservation:")) {
			// Extract restaurantID from the page name and pass it to the PlaceReservation component
			const restaurantID = parseInt(currentPage.substring("placeReservation:".length));
			return <PlaceReservation restaurantID={restaurantID} setPage={setPage} backPage={backPage}/>;
		} else if (currentPage.startsWith("placeFoodOrder:")) {
			// Extract restaurantID from the page name and pass it to the PlaceFoodOrder component
			const restaurantID = parseInt(currentPage.substring("placeFoodOrder:".length));
			return <PlaceFoodOrder restaurantID={restaurantID} setPage={setPage} backPage={backPage}/>;
		} else if (currentPage.startsWith("orderStatus:")) {
			// Extract foodOrderID from the page name and pass it to the OrderStatus component
			const foodOrderID = parseInt(currentPage.substring("orderStatus:".length));
			return <OrderStatus foodOrderID={foodOrderID} setPage={setPage} backPage={backPage}/>;
		} else if (currentPage == "restaurantControlPanel") {
			return <RestaurantControlPanel setPage={setPage} backPage={backPage}/>;
		} else if (currentPage == "orderQueue") {
			return <OrderQueue setPage={setPage} backPage={backPage}/>;
		} else {
			// Default page is home
			return <Home setPage={setPage}/>;
		}
	}

	return(
		<React.StrictMode>
			{/* The TopBar is present on every page, so is excluded from the page-displaying logic */}
			{<TopBar page={page} setPage={setPage} />}

			{/* The page-displaying logic */}
			{renderCurrentPage(page)}
		</React.StrictMode>
	);
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
	<App />
);