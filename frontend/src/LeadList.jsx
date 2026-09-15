import { useEffect, useState } from "react";
import { getLeads } from "./api";

// Couleur du badge selon la décision
function statusColor(status) {
  if (status === "qualifié") return "bg-green-100 text-green-800";
  if (status === "à nurturer") return "bg-yellow-100 text-yellow-800";
  if (status === "rejeté") return "bg-red-100 text-red-800";
  return "bg-gray-100 text-gray-700";
}

export default function LeadList({ onSelect }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getLeads()
      .then(setLeads)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-8 text-gray-500">Chargement...</p>;
  if (error) return <p className="p-8 text-red-600">{error}</p>;

  return (
    <div className="p-8">
      <h2 className="text-xl font-bold mb-4 text-gray-800">
        Pipeline des leads ({leads.length})
      </h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 text-left">
            <tr>
              <th className="px-4 py-3">Nom</th>
              <th className="px-4 py-3">Entreprise</th>
              <th className="px-4 py-3">Secteur</th>
              <th className="px-4 py-3">Score</th>
              <th className="px-4 py-3">Décision</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr
                key={lead.id}
                onClick={() => onSelect(lead.id)}
                className="border-t border-gray-100 hover:bg-blue-50 cursor-pointer"
              >
                <td className="px-4 py-3 font-medium">{lead.full_name}</td>
                <td className="px-4 py-3">{lead.company}</td>
                <td className="px-4 py-3">{lead.industry}</td>
                <td className="px-4 py-3">
                  {lead.score !== null ? lead.score : "—"}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor(
                      lead.status
                    )}`}
                  >
                    {lead.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}