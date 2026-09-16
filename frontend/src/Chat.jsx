import { useState, useEffect, useRef } from "react";
import { startChat, sendChatMessage } from "./api";

export default function Chat() {
  const [messages, setMessages] = useState([]); // {role, content}
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [complete, setComplete] = useState(false);
  const bottomRef = useRef(null);

  // Démarre la conversation au chargement de la page
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

  // Fait défiler vers le bas à chaque nouveau message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || loading || complete) return;

    const userMessage = input.trim();
    setInput("");
    // Affiche tout de suite le message du prospect
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
    <div className="min-h-screen bg-gray-100 flex flex-col items-center py-8">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow flex flex-col h-[80vh]">
        {/* En-tête */}
        <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
          <h1 className="font-bold">NeoMorIT</h1>
          <p className="text-sm text-blue-100">
            Assistant de qualification — parlez-nous de votre projet
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-gray-200 text-gray-800 rounded-bl-none"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-500 px-4 py-2 rounded-2xl text-sm">
                ...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Saisie */}
        <form onSubmit={handleSend} className="p-4 border-t border-gray-200 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={complete}
            placeholder={
              complete ? "Conversation terminée — merci !" : "Votre message..."
            }
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={loading || complete}
            className="bg-blue-600 text-white px-5 py-2 rounded-full text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            Envoyer
          </button>
        </form>
      </div>

      {complete && (
        <p className="mt-4 text-sm text-green-700">
          ✓ Votre demande a été transmise à notre équipe commerciale.
        </p>
      )}
    </div>
  );
}