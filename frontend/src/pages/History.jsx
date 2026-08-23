import { Clock3 } from "lucide-react";

export default function History() {
  return (
    <main className="placeholder-page">
      <div className="placeholder-icon">
        <Clock3 size={28} />
      </div>

      <h1>Search History</h1>

      <p>
        Previous semantic searches will appear here once
        the search API is connected.
      </p>

      <span className="coming-badge">
        Coming with retrieval integration
      </span>
    </main>
  );
}