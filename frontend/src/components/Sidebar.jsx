import {
  BookOpen,
  Clock3,
  FileText,
  LayoutDashboard,
  Search,
  Settings,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Search",
    path: "/search",
    icon: Search,
  },
  {
    label: "Sources",
    path: "/sources",
    icon: FileText,
  },
  {
    label: "History",
    path: "/history",
    icon: Clock3,
  },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <div
          className="sidebar-overlay"
          onClick={onClose}
        />
      )}

      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">
            <BookOpen size={21} />
          </div>

          <div>
            <strong>KnowBase</strong>
            <span>Personal AI Library</span>
          </div>

          <button
            className="mobile-close"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <p className="nav-label">WORKSPACE</p>

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}

          <p className="nav-label settings-label">
            SYSTEM
          </p>

          <NavLink
            to="/settings"
            onClick={onClose}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <Settings size={19} />
            <span>Settings</span>
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />

          <div>
            <strong>Knowledge Base</strong>
            <span>System connected</span>
          </div>
        </div>
      </aside>
    </>
  );
}