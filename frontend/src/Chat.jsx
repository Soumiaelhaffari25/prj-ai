import { useState, useEffect, useRef } from "react";
import { startChat, sendChatMessage } from "./api";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    startChat()
      .then((data) => {
        setConversationId(data.conversation_id);
        setMessages([{ role: "assistant", content: data.message }]);
      })
      .catch((err) =>
        setMessages([{ role: "assistant", content: "Erreur : " + err.message }])
      );
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || loading || complete) return;
    const userMessage = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMessage }]);
    setLoading(true);
    try {
      const res = await sendChatMessage(conversationId, userMessage);
      setMessages((m) => [...m, { role: "assistant", content: res.message }]);
      if (res.complete) setComplete(true);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Erreur : " + err.message },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="min-h-screen flex items-stretch"
      style={{
        background:
          "linear-gradient(135deg, #1F3A5F 0%, #162942 55%, #3B9FD8 100%)",
      }}
    >
      {/* ---- COLONNE GAUCHE : présentation NeoMorIT ---- */}
      <div className="hidden lg:flex flex-col justify-center w-3/5 px-12 text-white">
        <div className="flex items-center gap-3 mb-8">
          <img
            src="/logo.png"
            alt="NeoMorIT"
            className="h-14 w-auto bg-white rounded-xl p-1.5"
          />
          <span className="text-3xl font-extrabold">NeoMorIT</span>
        </div>

        <h1 className="text-4xl font-extrabold leading-tight mb-4">
          Donnons vie à votre projet digital.
        </h1>
        <p className="text-blue-100 text-lg mb-8 leading-relaxed">
          Agence digitale spécialisée en sites web, CRM, ERP et automatisation
          par l'intelligence artificielle. Nous aidons les entreprises à mieux
          vendre, mieux suivre leurs opérations et gagner du temps.
        </p>

        {/* Nos services */}
        <div className="space-y-3 mb-10">
          {[
            "Sites web et applications sur mesure",
            "CRM et ERP adaptés à votre activité",
            "Automatisation et intelligence artificielle",
          ].map((service, i) => (
            <div key={i} className="flex items-center gap-3">
              <span
                className="flex items-center justify-center h-6 w-6 rounded-full text-xs font-bold"
                style={{ backgroundColor: "#3B9FD8" }}
              >
                ✓
              </span>
              <span className="text-blue-50">{service}</span>
            </div>
          ))}
        </div>

        {/* Contact (Corrigé avec les balises <a>) */}
        <div className="border-t border-white/20 pt-6 text-sm text-blue-100 space-y-2">
          <p className="font-semibold text-white mb-2">
            Envie d'en savoir plus ?
          </p>
          <p>
            Site web :{" "}
            <a
              href="https://neomorit.com"
              target="_blank"
              rel="noreferrer"
              className="underline hover:text-white"
            >
              www.neomorit.com
            </a>
          </p>
          <p>
            Email :{" "}
            <a
              href="mailto:contact@neomorit.com"
              className="underline hover:text-white"
            >
              contact@neomorit.com
            </a>
          </p>
        </div>
      </div>

      {/* ---- COLONNE DROITE : le chat ---- */}
      <div className="w-full lg:w-3/5 flex flex-col">
        <div className="w-full bg-white shadow-2xl flex flex-col h-screen overflow-hidden">
          {/* En-tête du chat */}
          <div
            className="px-6 py-4 flex items-center gap-3"
            style={{
              background: "linear-gradient(135deg, #1F3A5F 0%, #2E5A8F 100%)",
            }}
          >
            <img
              src="/logo.png"
              alt="NeoMorIT"
              className="h-9 w-auto bg-white rounded-lg p-1"
            />
            <div>
              <h2 className="font-extrabold text-white">Assistant NeoMorIT</h2>
              <p className="text-xs text-blue-100">
                Parlez-nous de votre projet
              </p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-5 space-y-3 bg-gray-50">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm shadow-sm ${
                    msg.role === "user"
                      ? "text-white rounded-br-sm"
                      : "bg-white text-gray-800 rounded-bl-sm border border-gray-100"
                  }`}
                  style={
                    msg.role === "user" ? { backgroundColor: "#1F3A5F" } : {}
                  }
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-400 px-4 py-2.5 rounded-2xl text-sm border border-gray-100">
                  <span className="animate-pulse">NeoMorIT écrit...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Saisie */}
          <form
            onSubmit={handleSend}
            className="p-4 border-t border-gray-200 flex gap-2 bg-white"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={complete}
              placeholder={
                complete ? "Conversation terminée — merci !" : "Votre message..."
              }
              className="flex-1 border border-gray-200 rounded-full px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={loading || complete}
              className="text-white px-6 py-2.5 rounded-full text-sm font-semibold transition disabled:opacity-50"
              style={{ backgroundColor: "#3B9FD8" }}
            >
              Envoyer
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}