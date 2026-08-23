import { Search as SearchIcon, Sparkles } from "lucide-react";

export default function Search() {
  return (
    <main className="placeholder-page">
      <div className="placeholder-icon">
        <SearchIcon size={28} />
      </div>

      <h1>Semantic Search</h1>

      <p>
        Your intelligent retrieval interface will be
        connected here after the retrieval layer is
        integrated.
      </p>

      <span className="coming-badge">
        Retrieval integration in progress
      </span>
    </main>
  );
}