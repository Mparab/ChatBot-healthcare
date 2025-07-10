import React, { useState } from "react";
import "./App.css";

function App() {
  const [symptoms, setSymptoms] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);

    const symptomsArray = symptoms.split(",").map(s => s.trim()).filter(Boolean);

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms: symptomsArray })
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setResponse({ error: "Failed to get prediction." });
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Healthcare Chatbot</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Enter symptoms (comma separated):
          <input
            type="text"
            value={symptoms}
            onChange={e => setSymptoms(e.target.value)}
            placeholder="e.g. headache, fever, nausea"
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict Disease"}
        </button>
      </form>
      {response && (
        <div className="response">
          {response.error ? (
            <p style={{ color: "red" }}>{response.error}</p>
          ) : (
            <>
              <h2>Prediction:</h2>
              <p>Disease: <strong>{response.predicted_disease}</strong></p>
              <p>Recommended Medicines:</p>
              <ul>
                {response.recommended_medicines.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;