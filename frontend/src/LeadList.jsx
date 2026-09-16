import { useEffect, useState } from "react";
import { getLeads } from "./api";

function statusColor(status) {
  if (status === "qualifié") return "bg-green-100 text-green-800";
  if (status === "à nurturer") return "bg-amber-100 text-amber-800";
  if (status === "rejeté") return "bg-red-100 text-red-800";
  return "bg-gray-100 text-gray-700";
}

// Carte de statistique
function StatCard({ label, value, gradient }) {
  return (
    <div
      className="rounded-2xl p-5 text-white shadow-md"
      style={{ background: gradient }}
    >
      <p className="text-3xl font-extrabold">{value}</p>
      <p className="text-sm opacity-90 mt-1">{label}</p>
    </div>
  );
}

export default function LeadList({ onSelect }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function loadLeads() {
    getLeads()
      .then(setLeads)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadLeads();
  }, []);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/leads/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "new_lead") loadLeads();
    };
    return () => ws.close();
  }, []);

  if (loading) return <p className="p-8 text-gray-500">Chargement...</p>;
  if (error) return <p className="p-8 text-red-600">{error}</p>;

  // Calcul des statistiques
  const total = leads.length;
  const qualifies = leads.filter((l) => l.status === "qualifié").length;
  const nurture = leads.filter((l) => l.status === "à nurturer").length;
  const rejetes = leads.filter((l) => l.status === "rejeté").length;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-white">
        Pipeline des leads{" "}
        <span className="text-base font-normal text-gray-400">({total})</span>
      </h2>

      {/* Cartes de statistiques */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total des leads"
          value={total}
          gradient="linear-gradient(135deg, #3d71ba 0%, #6297d7 100%)"
        />
        <StatCard
          label="Qualifiés"
          value={qualifies}
          gradient="linear-gradient(135deg, #0c642c 0%, #199747 100%)"
        />
        <StatCard
          label="À nurturer"
          value={nurture}
          gradient="linear-gradient(135deg, #c06905 0%, #F59E0B 100%)"
        />
        <StatCard
          label="Rejetés"
          value={rejetes}
          gradient="linear-gradient(135deg, #ac1e1e 0%, #EF4444 100%)"
        />
      </div>

      {/* Tableau */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden">
        <table className="w-full text-sm">
          <thead
            style={{
              background: "linear-gradient(135deg, #1F3A5F 0%, #2E5A8F 100%)",
            }}
            className="text-white text-left"
          >
            <tr>
              <th className="px-5 py-4 font-semibold">Nom</th>
              <th className="px-5 py-4 font-semibold">Entreprise</th>
              <th className="px-5 py-4 font-semibold">Secteur</th>
              <th className="px-5 py-4 font-semibold">Score</th>
              <th className="px-5 py-4 font-semibold">Décision IA</th>
              <th className="px-5 py-4 font-semibold">Validation</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr
                key={lead.id}
                onClick={() => onSelect(lead.id)}
                className="border-t border-gray-100 hover:bg-blue-50 cursor-pointer transition"
              >
                <td className="px-5 py-4 font-medium text-gray-800">
                  {lead.full_name}
                </td>
                <td className="px-5 py-4 text-gray-600">{lead.company}</td>
                <td className="px-5 py-4 text-gray-600">{lead.industry}</td>
                <td className="px-5 py-4">
                  <span className="font-bold" style={{ color: "#1F3A5F" }}>
                    {lead.score !== null ? lead.score : "—"}
                  </span>
                </td>
                <td className="px-5 py-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColor(
                      lead.status
                    )}`}
                  >
                    {lead.status}
                  </span>
                </td>
                <td className="px-5 py-4">
                  {lead.review_status ? (
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        lead.review_status === "validé"
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {lead.review_status === "validé" ? "✓ validé" : "✗ rejeté"}
                    </span>
                  ) : (
                    <span className="text-gray-400 text-xs">en attente</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}