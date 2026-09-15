import { useEffect, useState } from "react";
import { getLead, processLead, reviewLead } from "./api";

function statusColor(status) {
  if (status === "qualifié") return "bg-green-100 text-green-800";
  if (status === "à nurturer") return "bg-yellow-100 text-yellow-800";
  if (status === "rejeté") return "bg-red-100 text-red-800";
  return "bg-gray-100 text-gray-700";
}

// Petite barre de progression pour un sous-score BANT
function ScoreBar({ label, value }) {
  return (
    <div className="mb-2">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{value}/100</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full"
          style={{ width: `${value}%` }}
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

  // Charge le lead au montage (et quand l'id change)
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

  // Lance le scoring (étape /process)
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

  // Valide ou rejette (étape /review)
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

  if (loading) return <p className="p-8 text-gray-500">Chargement...</p>;
  if (error) return <p className="p-8 text-red-600">{error}</p>;
  if (!lead) return null;

  // Parse le score_details (JSON stocké en texte)
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
        className="text-sm text-blue-600 hover:underline mb-4"
      >
        ← Retour au pipeline
      </button>

      {/* --- BILAN GLOBAL --- */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {lead.full_name}
            </h2>
            <p className="text-gray-500">
              {lead.job_title} — {lead.company}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-800">
              {lead.score !== null ? lead.score : "—"}
              <span className="text-base text-gray-400">/100</span>
            </div>
            <span
              className={`inline-block mt-1 px-3 py-1 rounded-full text-sm font-medium ${statusColor(
                lead.status
              )}`}
            >
              {lead.status}
            </span>
          </div>
        </div>
        {lead.assigned_to && (
          <p className="mt-4 text-sm text-gray-600">
            Assigné à : <span className="font-medium">{lead.assigned_to}</span>
          </p>
        )}
      </div>

      {/* --- PROFIL ENRICHI --- */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="font-bold text-gray-800 mb-3">Profil</h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div><span className="text-gray-500">Email :</span> {lead.email}</div>
          <div><span className="text-gray-500">Secteur :</span> {lead.industry}</div>
          <div><span className="text-gray-500">Taille :</span> {lead.company_size} employés</div>
          <div><span className="text-gray-500">CA :</span> {lead.annual_revenue} DH</div>
          <div className="col-span-2">
            <span className="text-gray-500">Signaux :</span> {lead.recent_signals || "—"}
          </div>
        </div>
      </div>

      {/* --- DÉTAIL DU SCORING --- */}
      {details && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-bold text-gray-800 mb-4">Détail du scoring</h3>

          {/* Couche BANT */}
          <div className="mb-6">
            <p className="text-sm font-semibold text-gray-700 mb-2">
              Règles BANT (déterministe) — {details.bant.score}/100
            </p>
            <ScoreBar label="Budget" value={details.bant.subscores.budget} />
            <ScoreBar label="Authority" value={details.bant.subscores.authority} />
            <ScoreBar label="Need" value={details.bant.subscores.need} />
            <ScoreBar label="Timing" value={details.bant.subscores.timing} />
          </div>

          {/* Couche LLM */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">
              Jugement IA (Groq/Llama) — {details.llm.score}/100
            </p>
            <p className="text-sm text-gray-600 italic mb-2">
              « {details.llm.reasoning} »
            </p>
            <p className="text-sm">
              <span className="text-gray-500">Intention :</span>{" "}
              <span className="font-medium">{details.llm.intent_level}</span>
            </p>
            {details.llm.risk_flags && details.llm.risk_flags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {details.llm.risk_flags.map((flag, i) => (
                  <span
                    key={i}
                    className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded"
                  >
                    {flag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* --- MESSAGE + VALIDATION --- */}
      {lead.status !== "rejeté" && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-bold text-gray-800 mb-3">
            Message d'approche
          </h3>
          {lead.action_message ? (
            <>
              <textarea
                value={editedMessage}
                onChange={(e) => setEditedMessage(e.target.value)}
                rows={6}
                className="w-full border border-gray-300 rounded p-3 text-sm mb-2"
              />
              {lead.review_status && (
                <p className="text-sm text-gray-500 mb-3">
                  Validation : <span className="font-medium">{lead.review_status}</span>
                  {lead.reviewed_by && ` par ${lead.reviewed_by}`}
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-gray-500">
              Aucun message généré. Lance le traitement pour en produire un.
            </p>
          )}
        </div>
      )}

      {/* --- ACTIONS --- */}
      <div className="flex gap-3">
        {lead.score === null && (
          <button
            onClick={handleProcess}
            disabled={working}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {working ? "Traitement..." : "Lancer le scoring"}
          </button>
        )}
        {lead.status !== "rejeté" && lead.action_message && (
          <>
            <button
              onClick={() => handleReview("valider")}
              disabled={working}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
            >
              Valider
            </button>
            <button
              onClick={() => handleReview("rejeter")}
              disabled={working}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
            >
              Rejeter
            </button>
          </>
        )}
      </div>
    </div>
  );
}