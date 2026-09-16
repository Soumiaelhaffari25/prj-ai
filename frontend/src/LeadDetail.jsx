import { useEffect, useState } from "react";
import { getLead, processLead, reviewLead } from "./api";

function statusColor(status) {
  if (status === "qualifié") return "bg-green-100 text-green-800";
  if (status === "à nurturer") return "bg-amber-100 text-amber-800";
  if (status === "rejeté") return "bg-red-100 text-red-800";
  return "bg-gray-100 text-gray-700";
}

// Barre de progression pour un sous-score BANT
function ScoreBar({ label, value }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-semibold" style={{ color: "#1F3A5F" }}>
          {value}/100
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2.5">
        <div
          className="h-2.5 rounded-full transition-all"
          style={{
            width: `${value}%`,
            background: "linear-gradient(90deg, #1F3A5F 0%, #3B9FD8 100%)",
          }}
        />
      </div>
    </div>
  );
}

export default function LeadDetail({ leadId, onBack, onUpdated }) {
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editedMessage, setEditedMessage] = useState("");
  const [working, setWorking] = useState(false);

  useEffect(() => {
    setLoading(true);
    getLead(leadId)
      .then((data) => {
        setLead(data);
        setEditedMessage(data.action_message || "");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [leadId]);

  async function handleProcess() {
    setWorking(true);
    try {
      const updated = await processLead(leadId);
      setLead(updated);
      setEditedMessage(updated.action_message || "");
      onUpdated && onUpdated();
    } catch (err) {
      setError(err.message);
    } finally {
      setWorking(false);
    }
  }

  async function handleReview(action) {
    setWorking(true);
    try {
      const updated = await reviewLead(leadId, action, editedMessage);
      setLead(updated);
      onUpdated && onUpdated();
    } catch (err) {
      setError(err.message);
    } finally {
      setWorking(false);
    }
  }

  if (loading) return <p className="p-8 text-white">Chargement...</p>;
  if (error) return <p className="p-8 text-red-200">{error}</p>;
  if (!lead) return null;

  let details = null;
  try {
    details = lead.score_details ? JSON.parse(lead.score_details) : null;
  } catch {
    details = null;
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <button
        onClick={onBack}
        className="text-sm text-blue-100 hover:text-white mb-4 transition"
      >
        ← Retour au pipeline
      </button>

      {/* --- BILAN GLOBAL --- */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold" style={{ color: "#1F3A5F" }}>
              {lead.full_name}
            </h2>
            <p className="text-gray-500">
              {lead.job_title} — {lead.company}
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-extrabold" style={{ color: "#1F3A5F" }}>
              {lead.score !== null ? lead.score : "—"}
              <span className="text-base text-gray-400">/100</span>
            </div>
            <span
              className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-semibold ${statusColor(
                lead.status
              )}`}
            >
              {lead.status}
            </span>
          </div>
        </div>
        {lead.assigned_to && (
          <div
            className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-600"
          >
            Assigné à :{" "}
            <span className="font-semibold" style={{ color: "#1F3A5F" }}>
              {lead.assigned_to}
            </span>
          </div>
        )}
      </div>

      {/* --- PROFIL --- */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
        <h3 className="font-bold mb-4" style={{ color: "#1F3A5F" }}>
          Profil
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-400">Email</span><p className="font-medium text-gray-800">{lead.email}</p></div>
          <div><span className="text-gray-400">Secteur</span><p className="font-medium text-gray-800">{lead.industry || "—"}</p></div>
          <div><span className="text-gray-400">Taille</span><p className="font-medium text-gray-800">{lead.company_size_raw || lead.company_size || "—"} employés</p></div>
          <div><span className="text-gray-400">Chiffre d'affaires</span><p className="font-medium text-gray-800">{lead.annual_revenue ? `${lead.annual_revenue.toLocaleString("fr-FR")} DH` : "—"}</p></div>
          <div className="col-span-2"><span className="text-gray-400">Signaux récents</span><p className="font-medium text-gray-800">{lead.recent_signals || "—"}</p></div>
        </div>
      </div>

      {/* --- DÉTAIL DU SCORING --- */}
      {details && (
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h3 className="font-bold mb-4" style={{ color: "#1F3A5F" }}>
            Détail du scoring
          </h3>

          <div className="mb-6">
            <p className="text-sm font-semibold text-gray-700 mb-3">
              Règles BANT (déterministe) —{" "}
              <span style={{ color: "#1F3A5F" }}>{details.bant.score}/100</span>
            </p>
            <ScoreBar label="Budget" value={details.bant.subscores.budget} />
            <ScoreBar label="Authority" value={details.bant.subscores.authority} />
            <ScoreBar label="Need" value={details.bant.subscores.need} />
            <ScoreBar label="Timing" value={details.bant.subscores.timing} />
          </div>

          <div className="pt-4 border-t border-gray-100">
            <p className="text-sm font-semibold text-gray-700 mb-2">
              Jugement IA (Groq/Llama) —{" "}
              <span style={{ color: "#3B9FD8" }}>{details.llm.score}/100</span>
            </p>
            <p className="text-sm text-gray-600 italic mb-3 bg-blue-50 p-3 rounded-lg">
              « {details.llm.reasoning} »
            </p>
            <p className="text-sm mb-2">
              <span className="text-gray-400">Intention :</span>{" "}
              <span className="font-semibold" style={{ color: "#1F3A5F" }}>
                {details.llm.intent_level}
              </span>
            </p>
            {details.llm.risk_flags && details.llm.risk_flags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {details.llm.risk_flags.map((flag, i) => (
                  <span
                    key={i}
                    className="bg-orange-100 text-orange-800 text-xs px-2.5 py-1 rounded-full"
                  >
                    {flag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* --- MESSAGE D'APPROCHE --- */}
      {lead.action_message && (
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h3 className="font-bold mb-3" style={{ color: "#1F3A5F" }}>
            Message d'approche
          </h3>
          <textarea
            value={editedMessage}
            onChange={(e) => setEditedMessage(e.target.value)}
            rows={7}
            className="w-full border border-gray-200 rounded-lg p-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
      )}

      {/* --- ACTIONS --- */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex flex-wrap gap-3 items-center">
          {lead.score === null && (
            <button
              onClick={handleProcess}
              disabled={working}
              className="text-white px-5 py-2.5 rounded-lg font-semibold transition disabled:opacity-50"
              style={{ backgroundColor: "#3B9FD8" }}
            >
              {working ? "Traitement..." : "Lancer le scoring"}
            </button>
          )}

          {lead.score !== null && (
            <>
              <button
                onClick={() => handleReview("valider")}
                disabled={working}
                className="bg-green-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
              >
                {lead.status === "rejeté" ? "Rattraper ce lead" : "Valider la proposition"}
              </button>
              <button
                onClick={() => handleReview("rejeter")}
                disabled={working}
                className="bg-red-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50"
              >
                {lead.status === "rejeté" ? "Confirmer le rejet" : "Rejeter la proposition"}
              </button>
            </>
          )}
        </div>

        {lead.score !== null && (
          <p className="mt-4 text-xs text-gray-500">
            Décision de l'IA : <span className="font-semibold">{lead.status}</span>
            {lead.review_status && (
              <>
                {" · "}Votre décision :{" "}
                <span className="font-semibold">{lead.review_status}</span>
              </>
            )}
          </p>
        )}
      </div>
    </div>
  );
}