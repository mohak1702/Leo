import { useState } from "react";
import {
  Mic,
  Send,
  Monitor,
  Globe2,
  Sparkles,
  Settings,
  Camera,
  Activity,
  Cpu,
} from "lucide-react";
import "./App.css";

function App() {
  const [command, setCommand] = useState("");
const [status, setStatus] = useState("READY");
const [activity, setActivity] = useState([]);

  const handleCommand = async () => {
  if (!command.trim()) return;

  const userCommand = command.trim();

  setStatus("THINKING");

  const commandEntry = {
    id: Date.now(),
    command: userCommand,
    status: "PROCESSING",
    response: null,
  };

  setActivity((prev) => [commandEntry, ...prev]);

  try {
    const response = await fetch("http://127.0.0.1:8000/command", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        command: userCommand,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();

    console.log("LEO backend response:", data);

    setActivity((prev) =>
      prev.map((item) =>
        item.id === commandEntry.id
          ? {
              ...item,
              status: "COMPLETED",
              response: data.message,
            }
          : item
      )
    );

    setStatus("READY");
    setCommand("");
  } catch (error) {
    console.error("LEO backend error:", error);

    setActivity((prev) =>
      prev.map((item) =>
        item.id === commandEntry.id
          ? {
              ...item,
              status: "ERROR",
              response: "Unable to communicate with LEO backend.",
            }
          : item
      )
    );

    setStatus("READY");
  }
};

  return (
    <div className={`leo-app status-${status.toLowerCase()}`}>
      {/* Digital Shower Matrix-Style Rain Streams */}
      <div className="digital-shower-bg">
        <div className="shower-stream"></div>
        <div className="shower-stream"></div>
        <div className="shower-stream"></div>
        <div className="shower-stream"></div>
        <div className="shower-stream"></div>
        <div className="shower-stream"></div>
      </div>

      {/* Sci-Fi Screen Corner Brackets */}
      <div className="hud-corner top-left"></div>
      <div className="hud-corner top-right"></div>
      <div className="hud-corner bottom-left"></div>
      <div className="hud-corner bottom-right"></div>

      <header className="top-bar">
        <div className="brand">
          <div className="brand-symbol">L</div>
          <div>
            <h1>LEO</h1>
            <p>LOCAL EXECUTION & ORCHESTRATION</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          {status === "THINKING" ? "PROCESSING ACTION..." : "SYSTEM ONLINE"}
        </div>

        <button className="icon-button">
          <Settings size={20} />
        </button>
      </header>

      <main className="main-content">
        <section className="assistant-section">
          {/* Main Visual Arc Core / Orb */}
          <div className="orb-wrapper">
            <div className="orb-ring ring-one"></div>
            <div className="orb-ring ring-two"></div>
            <div className="orb-ring ring-three"></div>
            <div className="orb-scanline"></div>

            <div className="leo-orb">
              <div className="orb-core-lines"></div>
              <div className="orb-text-overlay">
                <span>{status === "THINKING" ? "PROCESSING" : "SYSTEM READY"}</span>
              </div>
            </div>
          </div>

          <div className="assistant-title">
            <span className="small-line"></span>
            <Cpu size={12} />
            <span>AI CORE ENGINE</span>
            <span className="small-line"></span>
          </div>

          <h2>How can I assist?</h2>

          <div className={`leo-status ${status.toLowerCase()}`}>
            <span></span>
            {status}
          </div>

          <div className="command-container">
            <button
              className="voice-button"
              onClick={() => setStatus(status === "LISTENING" ? "READY" : "LISTENING")}
            >
              <Mic size={22} />
            </button>

            <input
              type="text"
              placeholder="Ask LEO to run local tasks or web automations..."
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCommand();
              }}
            />

            <button className="send-button" onClick={handleCommand}>
              <Send size={19} />
            </button>
          </div>

          <div className="quick-actions">
            <button>
              <Monitor size={17} />
              <span>Computer</span>
            </button>
            <button>
              <Globe2 size={17} />
              <span>Browser</span>
            </button>
            <button>
              <Camera size={17} />
              <span>Vision</span>
            </button>
            <button>
              <Sparkles size={17} />
              <span>AI Tasks</span>
            </button>
          </div>
        </section>

        <aside className="activity-panel">
          <div className="panel-heading">
            <div>
              <Activity size={16} />
              <span>LEO TELEMETRY</span>
            </div>
            <span className="live-badge">LIVE</span>
          </div>

          <div className="activity-feed">
  {activity.length === 0 ? (
    <div className="activity-empty">
      <div className="activity-icon">
        <Sparkles size={24} />
      </div>

      <h3>Standing by</h3>

      <p>
        Give LEO a command to watch live device execution in real-time.
      </p>
    </div>
  ) : (
    activity.map((item) => (
      <div className="activity-item" key={item.id}>
        <div className="activity-item-header">
          <span>COMMAND</span>
          <span>{item.status}</span>
        </div>

        <div className="activity-command">
          &gt; {item.command}
        </div>

        {item.response && (
          <div className="activity-response">
            {item.response}
          </div>
        )}
      </div>
    ))
  )}
</div>

          <div className="capability-grid">
            <div>
              <span className="capability-dot"></span>
              <section>
                <strong>Computer</strong>
                <p>Ready</p>
              </section>
            </div>
            <div>
              <span className="capability-dot"></span>
              <section>
                <strong>Browser</strong>
                <p>Ready</p>
              </section>
            </div>
            <div>
              <span className="capability-dot inactive"></span>
              <section>
                <strong>Vision</strong>
                <p>Standby</p>
              </section>
            </div>
            <div>
              <span className="capability-dot inactive"></span>
              <section>
                <strong>Voice</strong>
                <p>Standby</p>
              </section>
            </div>
          </div>
        </aside>
      </main>

      <footer>
        <span>LEO CORE v0.1</span>
        <span>HUD ENGINE ACTIVE</span>
      </footer>
    </div>
  );
}

export default App;