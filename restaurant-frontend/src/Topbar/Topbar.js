import './Topbar.css';

function UserButton() {
    // This component should allow the user to view their profile or sign in
    return (
        <div className="userButton">
            <t>Account</t>
        </div>
    );
}

export default function TopBar() {
    return (
        <div className="topbar">
            <div className="topbarTitle">
                <t>TableNest</t>
            </div>
            <div className="userButtonContainer">
                <UserButton />
            </div>
        </div>
    );
}