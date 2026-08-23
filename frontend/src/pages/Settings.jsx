import { Settings as SettingsIcon } from "lucide-react";

export default function Settings() {
  return (
    <main className="placeholder-page">
      <div className="placeholder-icon">
        <SettingsIcon size={28} />
      </div>

      <h1>Settings</h1>

      <p>
        Workspace and account settings will be added in
        the next frontend stage.
      </p>

      <span className="coming-badge">
        Coming soon
      </span>
    </main>
  );
}