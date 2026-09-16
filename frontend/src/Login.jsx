import { useState } from "react";
import { login } from "./api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      onLogin();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background:
          "linear-gradient(135deg, #1F3A5F 0%, #162942 55%, #3B9FD8 100%)",
      }}
    >
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8"
      >
        {/* Logo image + texte */}
        <div className="flex items-center justify-center gap-3 mb-1">
          <img src="/logo.png" alt="NeoMorIT" className="h-12 w-auto" />
          <div>
            <span className="text-3xl font-extrabold" style={{ color: "#1F3A5F" }}>
              NeoMor
            </span>
            <span className="text-3xl font-extrabold" style={{ color: "#3B9FD8" }}>
              IT
            </span>
          </div>
        </div>
        <p className="text-center text-gray-400 mb-8 text-sm">
          Espace commercial — Qualification des leads
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 p-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-4 py-2.5 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
          required
        />

        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Mot de passe
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-4 py-2.5 mb-6 focus:outline-none focus:ring-2 focus:ring-blue-300"
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full text-white py-3 rounded-lg font-semibold transition disabled:opacity-50"
          style={{ backgroundColor: "#1F3A5F" }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#162942")}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#1F3A5F")}
        >
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </div>
  );
}