import { useState } from "react";
import { isLoggedIn, logout } from "./api";
import Login from "./Login";
import LeadList from "./LeadList";
import LeadDetail from "./LeadDetail";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());
  const [selectedId, setSelectedId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div
      className="min-h-screen"
      style={{
        background:
          "linear-gradient(135deg, #1F3A5F 0%, #162942 55%, #3B9FD8 100%)",
      }}
    >
      <header className="bg-white shadow-sm px-8 py-4 flex justify-between items-center border-b border-gray-100">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="NeoMorIT" className="h-9 w-auto" />
          <div>
            <span className="text-lg font-extrabold" style={{ color: "#1F3A5F" }}>
              NeoMor
            </span>
            <span className="text-lg font-extrabold" style={{ color: "#3B9FD8" }}>
              IT
            </span>
            <p className="text-xs text-gray-400 -mt-1">
              Qualification des leads
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            logout();
            setLoggedIn(false);
          }}
          className="text-sm font-semibold text-white px-4 py-2 rounded-lg transition"
          style={{ backgroundColor: "#1F3A5F" }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#162942")}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#1F3A5F")}
        >
          Se déconnecter
        </button>
      </header>

      {selectedId ? (
        <LeadDetail
          key={selectedId}
          leadId={selectedId}
          onBack={() => setSelectedId(null)}
          onUpdated={() => setRefreshKey((k) => k + 1)}
        />
      ) : (
        <LeadList key={refreshKey} onSelect={setSelectedId} />
      )}
    </div>
  );
}