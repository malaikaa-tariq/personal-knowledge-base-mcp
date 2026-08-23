import { Bell, Menu, Search } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Topbar({ onMenuClick }) {
  const { user } = useAuth();

  const name =
    user?.full_name ||
    user?.email?.split("@")[0] ||
    "User";

  const initial = name.charAt(0).toUpperCase();

  return (
    <header className="topbar">
      <button
        className="menu-button"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu size={22} />
      </button>

      <div className="topbar-search">
        <Search size={18} />

        <input
          type="text"
          placeholder="Search your knowledge..."
          readOnly
        />
      </div>

      <div className="topbar-actions">
        <button className="icon-button">
          <Bell size={19} />
        </button>

        <div className="user-profile">
          <div className="avatar">
            {initial}
          </div>

          <div className="user-info">
            <strong>{name}</strong>
            <span>{user?.email}</span>
          </div>
        </div>
      </div>
    </header>
  );
}