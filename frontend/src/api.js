// Toutes les communications avec le backend NeoMorIT passent par ici.
const API_URL = "http://localhost:8000";

// Récupère le token stocké dans le navigateur
function getToken() {
  return localStorage.getItem("token");
}

// --- Authentification ---
export async function login(email, password) {
  // OAuth2 attend un format "form-urlencoded" avec username/password
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Email ou mot de passe incorrect");
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  return data;
}

export function logout() {
  localStorage.removeItem("token");
}

export function isLoggedIn() {
  return !!getToken();
}

// --- Leads ---
export async function getLeads() {
  const res = await fetch(`${API_URL}/leads`);
  if (!res.ok) throw new Error("Erreur lors du chargement des leads");
  return res.json();
}

export async function getLead(id) {
  const res = await fetch(`${API_URL}/leads/${id}`);
  if (!res.ok) throw new Error("Lead introuvable");
  return res.json();
}

export async function processLead(id) {
  const res = await fetch(`${API_URL}/leads/${id}/process`, { method: "POST" });
  if (!res.ok) throw new Error("Erreur lors du traitement");
  return res.json();
}

// --- Validation (route protégée : nécessite le token) ---
export async function reviewLead(id, action, editedMessage = null) {
  const res = await fetch(`${API_URL}/leads/${id}/review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ action, edited_message: editedMessage }),
  });
  if (!res.ok) throw new Error("Erreur lors de la validation");
  return res.json();
}

// --- Chatbot (public, pas de token) ---
export async function startChat() {
  const res = await fetch(`${API_URL}/chat/start`, { method: "POST" });
  if (!res.ok) throw new Error("Impossible de démarrer la conversation");
  return res.json();
}

export async function sendChatMessage(conversationId, message) {
  const res = await fetch(`${API_URL}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, message }),
  });
  if (!res.ok) throw new Error("Erreur lors de l'envoi du message");
  return res.json();
}