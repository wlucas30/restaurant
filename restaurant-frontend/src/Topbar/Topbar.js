import './Topbar.css';

function UserButton({ setPage }) {
    // This component contains a button which changes the displayed page to account page
    return (
        <div className="userButton" onClick={() => setPage("account")}>
            <t>Account</t>
        </div>
    );
}

export default function TopBar({ page, setPage }) {
    return (
        <div className="topbar">
            <div className="topbarTitle">
                <t>TableNest</t>
            </div>
            <div className="userButtonContainer">
                <UserButton setPage={setPage}/>
            </div>
        </div>
    );
}