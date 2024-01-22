import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Home from './Home/Home';
import TopBar from './Topbar/Topbar';
import reportWebVitals from './reportWebVitals';

// Initialise a state variable which determines the currently displayed page
const [page, setPage] = useState("home"); // default page is the home page

// This function evaluates the current value of the page state variable and returns the appropriate page component
function renderCurrentPage(currentPage) {
	switch (currentPage) {
		case "home":
			return <Home />;
		default:
			return <Home />;
	}
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
	<React.StrictMode>
    	{/* The TopBar is present on every page, so is excluded from the page-displaying logic */}
    	<TopBar page={page} setPage={setPage} />

    	{/* The page-displaying logic */}
		{renderCurrentPage(page)}
  	</React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
