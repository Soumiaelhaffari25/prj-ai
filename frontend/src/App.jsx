import { useState } from "react";
import { isLoggedIn, logout } from "./api";
import Login from "./Login";
import LeadList from "./LeadList";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());
  const [selectedId, setSelectedId] = useState(null);

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow px-8 py-4 flex justify-between items-center">
        <h1 className="text-lg font-bold text-gray-800">
          NeoMorIT — Qualification des leads
        </h1>
        <button
          onClick={() => {
            logout();
            setLoggedIn(false);
          }}
          className="text-sm text-gray-500 hover:text-gray-800"
        >
          Se déconnecter
        </button>
      </header>

      <LeadList onSelect={setSelectedId} />
    </div>
  );
}