import { useMemo, useState } from "react";

const DEFAULT_TEXT =
  ``;

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function labelFor(score) {
  if (score >= 70) return "RED";
  if (score >= 40) return "YELLOW";
  return "GREEN";
}

function classesFor(label) {
  switch (label) {
    case "RED":
      return { pill: "pill pill-red", ring: "ring-red" };
    case "YELLOW":
      return { pill: "pill pill-yellow", ring: "ring-yellow" };
    default:
      return { pill: "pill pill-green", ring: "ring-green" };
  }
}

function ResultCard({ judgement }) {
  const score = clamp(judgement?.ai_likelihood_score ?? 0, 0, 100);
  const label = labelFor(score);
  const ui = classesFor(label);

  return (
    <section className={`card ${ui.ring} resultCard`}>
      <div className="resultHeader">
        <h2 className="h2">Result</h2>
        <span
          className={ui.pill}
          title={judgement?.model ? `Model: ${judgement.model}` : "Model: (unknown)"}
        >
          {label}
        </span>
      </div>

      <div className="scoreOnly">
        <div className="score">{score}%</div>
      </div>

      <div className="divider" />

      <div className="reasoning">
        <div className="sectionTitle">Explanation</div>
        <p className="reasoningText">{judgement?.reasoning || "—"}</p>

        {Array.isArray(judgement?.signals) && judgement.signals.length > 0 && (
          <>
            <div className="sectionTitle">Signals</div>
            <ul className="list">
              {judgement.signals.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </>
        )}

        {Array.isArray(judgement?.evidence) && judgement.evidence.length > 0 && (
          <>
            <div className="sectionTitle">Evidence</div>
            <ul className="list">
              {judgement.evidence.map((e, i) => (
                <li key={i}>&ldquo;{e}&rdquo;</li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}


export default function App() {
  const [text, setText] = useState(DEFAULT_TEXT);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const judgements = useMemo(() => result?.per_model || [], [result]);

  const best = useMemo(() => {
    if (!judgements.length) return null;
    return judgements.reduce((max, cur) =>
      (cur.ai_likelihood_score ?? -1) > (max.ai_likelihood_score ?? -1) ? cur : max
    );
  }, [judgements]);

  // Keep an ordered list: Top first, then the rest (stable order)
  const ordered = useMemo(() => {
    if (!best) return [];
    const rest = judgements.filter((j) => j !== best);
    return [best, ...rest];
  }, [judgements, best]);

  async function analyze() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Same-origin call (works with Vite proxy in dev, and /api in prod)
      const res = await fetch("https://textonomy.onrender.com/api/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(data?.details || data?.error || `HTTP ${res.status}`);
      }

      setResult(data);
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <div className="logo">&#x1F50D;</div>
          <div>
            <div className="title">textonomy</div>
            <div className="subtitle">Human or machine – the odds are in.</div>
          </div>
        </div>
      </header>

      <main className="container">
        <section className="card">
          <h1 className="h1">Analyze text</h1>
          <p className="muted">
            Analyzed by several AI models with the highest risk score displayed &rarr;
          </p>

          <label className="label" htmlFor="text">
            Text
          </label>
          <textarea
            id="text"
            className="textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste text here…"
            rows={10}
          />

          <div className="row">
              <button className="btn" onClick={analyze} disabled={loading || !text.trim()}>
                {loading ? "Analyzing…" : "Analyze"}
              </button>

              <div className={`loaderBar ${loading ? "isLoading" : ""}`} aria-hidden="true">
                <div className="loaderBarFill" />
              </div>
            

          </div>

          {error && (
            <div className="error">
              <div className="errorTitle">Request failed</div>
              <div className="errorBody">{error}</div>
            </div>
          )}
        </section>

        <div className="resultsStack">
          {!best && (
            <section className="card">
              <div className="empty">No result yet. Run an analysis to see the results.</div>
            </section>
          )}

          {ordered.length > 0 && (
            <>
              {ordered.map((j, idx) => (
                <ResultCard key={`${j.model}-${idx}`} judgement={j} />
              ))}
            </>
          )}

        </div>
      </main>

      <footer className="footer">
        <span className="muted">This is an indicator — not proof.</span>

                          <div className="copyright">
          <span className="url">textonomy-1.onrender.com</span>
        </div>
          <div className="copyright">
          Copyright &copy; L.J Bergman
        </div>
      </footer>
    </div>
  );
}
