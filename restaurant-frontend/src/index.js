import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Home from './Home/Home';
import TopBar from './Topbar/Topbar';

function App() {
	// Initialise a state variable which determines the currently displayed page
	const [page, setPage] = useState("home"); // default page is the home page

	// This function evaluates the current value of the page state variable and returns the appropriate page component
	function renderCurrentPage(currentPage) {
		if (currentPage == "home") {
			return <Home setPage={setPage}/>;
		/*} else if (currentPage.startsWith("viewRestaurantDetails:")) {
			// Extract restaurantID from the page name and pass it to the RestaurantDetails component
			const restaurantID = parseInt(currentPage.substring("viewRestaurantDetails:".length));
			return <RestaurantPreview restaurantID={restaurantID} setPage={setPage}/>;
		*/} else {
			// Default page is home
			return <Home setPage={setPage}/>;
		}
	}

	const root = ReactDOM.createRoot(document.getElementById("root"));
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