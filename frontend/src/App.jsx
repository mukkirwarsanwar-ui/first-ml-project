import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function scoreColor(score) {
  if (score >= 70) return "#16a34a";
  if (score >= 40) return "#d97706";
  return "#dc2626";
}

export default function App() {
  const [job, setJob] = useState("");
  const [files, setFiles] = useState([]);
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadHistory() {
    try {
      const res = await fetch(`${API_URL}/jobs`);
      if (res.ok) setHistory(await res.json());
    } catch {
      // history is optional, so ignore failures
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function openJob(id) {
    setError("");
    try {
      const res = await fetch(`${API_URL}/jobs/${id}`);
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail || "Could not load job");
      setData(body);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleSubmit() {
    setError("");
    setData(null);

    if (!job.trim() || files.length === 0) {
      setError("Add a job description and at least one PDF resume.");
      return;
    }

    const form = new FormData();
    form.append("job_description", job);
    files.forEach((f) => form.append("files", f));

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/match`, { method: "POST", body: form });
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail || "Request failed");
      setData(body);
      loadHistory();
    } catch (e) {
      setError(e.message || "Could not reach the server");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Resume Matcher</h1>
      <p className="sub">Rank resumes against a job description using AI.</p>

      <div className="card">
        <label>Job description</label>
        <textarea
          rows={6}
          value={job}
          onChange={(e) => setJob(e.target.value)}
          placeholder="Paste the job description here..."
        />

        <label>Resumes (PDF)</label>
        <input
          type="file"
          accept=".pdf"
          multiple
          onChange={(e) => setFiles(Array.from(e.target.files))}
        />
        {files.length > 0 && <p className="hint">{files.length} file(s) selected</p>}

        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Analyzing..." : "Rank candidates"}
        </button>

        {error && <p className="error">{error}</p>}
      </div>

      {data && (
        <div>
          <h2>Results</h2>
          <p className="hint">
            Required skills: {(data.required_skills || []).join(", ") || "none detected"}
          </p>

          {data.results.map((r, i) => (
            <div className="card" key={r.file}>
              <div className="row">
                <strong>
                  #{i + 1} {r.file}
                </strong>
                <span className="score" style={{ color: scoreColor(r.final_score) }}>
                  {r.final_score}%
                </span>
              </div>

              <div className="bar">
                <div
                  className="fill"
                  style={{
                    width: `${r.final_score}%`,
                    background: scoreColor(r.final_score),
                  }}
                />
              </div>
              <p className="hint">
                Meaning match {r.meaning_score}% | Skill match {r.skill_score}%
              </p>

              <div className="chips">
                {(r.matched_skills || []).map((s) => (
                  <span key={s} className="chip good">{s}</span>
                ))}
                {(r.missing_skills || []).map((s) => (
                  <span key={s} className="chip bad">{s}</span>
                ))}
              </div>
            </div>
          ))}

          {(data.skipped || []).length > 0 && (
            <p className="error">
              Skipped: {data.skipped.map((s) => `${s.file} (${s.reason})`).join(", ")}
            </p>
          )}
        </div>
      )}

      <h2>Past jobs</h2>
      {history.length === 0 && <p className="hint">No saved jobs yet.</p>}
      {history.map((j) => (
        <div className="card history-item" key={j.id} onClick={() => openJob(j.id)}>
          <strong>{j.title}</strong>
          <p className="hint">
            {new Date(j.created_at).toLocaleString()} | {(j.required_skills || []).join(", ")}
          </p>
        </div>
      ))}
    </div>
  );
}