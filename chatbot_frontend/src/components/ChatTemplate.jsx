// chatbot_frontend/src/components/ChatTemplate.jsx
import { useEffect, useRef, useState } from "react";
import "../chatbot.css";

export default function ChatTemplate({
  apiEndpoint,
  headerTitle,
  suggestions,
  routeName
}) {
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesRef = useRef();

  // ------------------------------
  // AUTO-CREATE CHAT WHEN PAGE OPENS
  // ------------------------------
  useEffect(() => {
    fetchChats().then(() => {
      createNewChat();  // start new chat automatically
    });
  }, []);

  useEffect(() => {
    if (messagesRef.current)
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
  }, [messages]);

  // ------------------------------
  // FETCH CHAT LIST
  // ------------------------------
  async function fetchChats() {
    const res = await fetch("http://127.0.0.1:5002/api/chat/list");
    const data = await res.json();
    setChats(data.chats || []);
  }

  // ------------------------------
  // CREATE NEW CHAT
  // ------------------------------
  async function createNewChat() {
    const res = await fetch("http://127.0.0.1:5002/api/chat/new", {
      method: "POST",
    });
    const data = await res.json();

    if (data.chat_id) {
      await fetchChats();
      selectChat(data.chat_id);
    }
  }

  // ------------------------------
  // LOAD A CHAT
  // ------------------------------
  async function selectChat(chatId) {
    setActiveChat(null);
    setMessages([]);

    const res = await fetch(
      `http://127.0.0.1:5002/api/chat/${chatId}/messages`
    );
    const data = await res.json();

    setActiveChat({
      id: chatId,
      title: chats.find((c) => c.id === chatId)?.title || "Chat",
    });

    setMessages(
      (data.messages || []).map((m) => ({
        from: m.sender === "user" ? "user" : "bot",
        text: m.text,
      }))
    );
  }

  // ------------------------------
  // SEND MESSAGE FUNCTION
  // ------------------------------
  async function sendMessage(text) {
    if (!text.trim() || !activeChat) return;

    setMessages((prev) => [...prev, { from: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(apiEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: activeChat.id,
          message: text,
        }),
      });

      const data = await res.json();
      const reply = data.reply || "[No response]";

      setMessages((prev) => [...prev, { from: "bot", text: reply }]);

      // Generate chat title for first message
      const currentChat = chats.find((c) => c.id === activeChat.id);
      if (currentChat && currentChat.title === "New Chat") {
        await fetch("http://127.0.0.1:5002/api/chat/title", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: activeChat.id,
            message: text,
          }),
        });
        await fetchChats();
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "Server error. Try again." },
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="chat-wrapper">
      {/* LEFT SIDEBAR */}
      <aside className="chat-sidebar">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <strong style={{ fontSize: 18 }}>{routeName}</strong>
          <button className="btn-new" onClick={createNewChat}>
            + New Chat
          </button>
        </div>

        <div style={{ marginTop: 12, overflowY: "auto", flex: 1 }}>
          {chats.length === 0 && (
            <p style={{ color: "var(--muted)", fontSize: 13 }}>No chats yet</p>
          )}

          {chats.map((c) => (
            <div
              key={c.id}
              className="chat-item"
              onClick={() => selectChat(c.id)}
              style={{
                background:
                  activeChat && activeChat.id === c.id
                    ? "rgba(255,255,255,0.05)"
                    : "transparent",
              }}
            >
              <div className="icon">
                {String(c.title || "C").slice(0, 2).toUpperCase()}
              </div>
              <div>
                <div style={{ fontWeight: 700 }}>
                  {c.title || "New Chat"}
                </div>
                <div
                  style={{
                    fontSize: 12,
                    color: "rgba(255,255,255,0.6)",
                  }}
                >
                  {new Date(c.created_at).toLocaleString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* MAIN CHAT PANEL */}
      <section className="chat-panel">
        <div className="panel-header">
          <div>
            <h2 style={{ margin: 0 }}>{headerTitle}</h2>
            <div className="panel-sub">Ask anything and get expert guidance</div>
          </div>
        </div>

        {/* SUGGESTIONS ONLY WHEN EMPTY */}
        {messages.length === 0 && (
          <div style={{ display: "flex", gap: 12, margin: "16px 0" }}>
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={async () => {
                  if (!activeChat) {
                    await createNewChat();
                    setTimeout(() => sendMessage(s), 200);
                  } else {
                    sendMessage(s);
                  }
                }}
                style={{
                  padding: "12px 18px",
                  background: "var(--card)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 12,
                  color: "#fff",
                  cursor: "pointer",
                }}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* MESSAGES */}
        <div className="messages" ref={messagesRef}>
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.from}`}>
              <div
                className="msg-content"
                dangerouslySetInnerHTML={{
                  __html: m.text
                    .replace(/\n/g, "<br/>")
                    .replace(/- /g, "• "),
                }}
              ></div>
            </div>
          ))}
        </div>

        {/* INPUT */}
        <div className="input-area">
          <input
            placeholder={`Ask the ${headerTitle}...`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && sendMessage(input)
            }
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!activeChat || loading}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </section>
    </div>
  );
}
