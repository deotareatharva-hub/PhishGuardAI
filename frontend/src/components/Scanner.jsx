
import { useState } from "react";
import {
  ScanSearch,
  ShieldCheck,
  ShieldAlert,
  LoaderCircle,
  ArrowUpRight,
  AlertTriangle,
  CheckCircle2,
  Activity,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

// Dataset label mapping:
// Class 0 = Phishing
// Class 1 = Legitimate

export default function Scanner() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleScan(event) {
    event.preventDefault();

    setResult(null);
    setError("");

    const inputUrl = url.trim();

    if (!inputUrl) {
      setError("Please enter a URL to scan.");
      return;
    }

    // Basic URL validation
    let parsedUrl;

    try {
      const normalizedUrl = /^https?:\/\//i.test(inputUrl)
        ? inputUrl
        : `https://${inputUrl}`;

      parsedUrl = new URL(normalizedUrl);

      if (
        !["http:", "https:"].includes(parsedUrl.protocol) ||
        !parsedUrl.hostname.includes(".")
      ) {
        throw new Error("invalid");
      }
    } catch {
      setError(
        "Please enter a valid website URL, such as https://example.com."
      );
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/api/scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: parsedUrl.href }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const message =
          typeof data?.detail === "string"
            ? data.detail
            : "Unable to scan this URL. Please try again.";

        throw new Error(message);
      }

      // Validate the response before rendering it.
      if (
        !data ||
        ![0, 1].includes(Number(data.predicted_class)) ||
        typeof data.predicted_class_probability !== "number" ||
        !data.class_probabilities ||
        !data.features
      ) {
        throw new Error(
          "The API returned an unexpected response format."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the API. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  const predictedClass =
    result == null ? null : Number(result.predicted_class);

  const isPhishing = predictedClass === 0;
  const confidence = result
    ? Number(result.predicted_class_probability) * 100
    : 0;

  const classProbabilities = result
    ? Object.entries(result.class_probabilities).sort(
        ([labelA], [labelB]) => Number(labelA) - Number(labelB)
      )
    : [];

  return (
    <section className="scanner-panel">
      {/* Scanner heading */}
      <div className="section-heading">
        <div>
          <span className="eyebrow">THREAT DETECTION</span>
          <h2>URL Security Scanner</h2>
          <p>Analyze a URL using the trained SVD + MLP model.</p>
        </div>

        <div className="scanner-heading-icon">
          <ScanSearch size={23} />
        </div>
      </div>

      {/* URL input form */}
      <form onSubmit={handleScan} className="scanner-form">
        <label htmlFor="scan-url">Website URL</label>

        <div className="url-input-wrap">
          <input
            id="scan-url"
            type="text"
            value={url}
            onChange={(event) => {
              setUrl(event.target.value);

              if (error) {
                setError("");
              }
            }}
            placeholder="https://example.com"
            autoComplete="url"
            spellCheck={false}
            disabled={loading}
            aria-describedby="scan-url-hint"
          />

          <button
            type="submit"
            disabled={loading}
            className="scan-button"
          >
            {loading ? (
              <LoaderCircle size={18} className="spin" />
            ) : (
              <ScanSearch size={18} />
            )}

            {loading ? "Analyzing..." : "Scan URL"}
          </button>
        </div>

        <p id="scan-url-hint" className="input-hint">
          Enter a website URL to analyze its extracted features.
        </p>
      </form>

      {/* Error message */}
      {error && (
        <div className="error-box" role="alert">
          <AlertTriangle size={19} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="scanner-loading" role="status">
          <LoaderCircle size={24} className="spin" />
          <div>
            <strong>Analyzing URL...</strong>
            <p>Extracting features and running the SVD + MLP model.</p>
          </div>
        </div>
      )}

      {/* Prediction result */}
      {result && (
        <div className="scan-result">
          <div className="result-top">
            <div
              className={`result-icon ${
                isPhishing
                  ? "result-icon-danger"
                  : "result-icon-safe"
              }`}
            >
              {isPhishing ? (
                <ShieldAlert size={25} />
              ) : (
                <ShieldCheck size={25} />
              )}
            </div>

            <div className="result-copy">
              <span className="eyebrow">MODEL PREDICTION</span>

              <h3>
                {isPhishing
                  ? "Phishing Detected"
                  : "Legitimate URL"}
              </h3>

              <p>
                {isPhishing
                  ? "The model classified this URL as phishing. Avoid interacting with it until independently verified."
                  : "The model classified this URL as legitimate. This prediction does not guarantee that the website is safe."}
              </p>
            </div>

            <span
              className={`result-badge ${
                isPhishing
                  ? "result-badge-danger"
                  : "result-badge-safe"
              }`}
            >
              {confidence.toFixed(2)}% confidence
            </span>
          </div>

          {/* Scanned URL */}
          <div className="result-url">
            <span>Scanned URL</span>

            <div className="scanned-url-value">
              <code>{result.url || url}</code>

              <a
                href={result.url || url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Open scanned URL in a new tab"
                title="Open scanned URL"
              >
                <ArrowUpRight size={17} />
              </a>
            </div>
          </div>

          {/* Class probabilities */}
          <div className="probability-section">
            <div className="subsection-heading">
              <h4>Prediction Probabilities</h4>
              <Activity size={18} />
            </div>

            <div className="probability-grid">
              {classProbabilities.map(([label, probability]) => {
                const classNumber = Number(label);
                const phishingClass = classNumber === 0;
                const percentage = Math.max(
                  0,
                  Math.min(100, Number(probability) * 100)
                );

                return (
                  <div
                    className={`probability-card ${
                      phishingClass
                        ? "probability-card-danger"
                        : "probability-card-safe"
                    }`}
                    key={label}
                  >
                    <div className="probability-card-heading">
                      <span>
                        {phishingClass
                          ? "Phishing (Class 0)"
                          : "Legitimate (Class 1)"}
                      </span>

                      <strong>{percentage.toFixed(2)}%</strong>
                    </div>

                    <div className="probability-track">
                      <div
                        className={`probability-fill ${
                          phishingClass
                            ? "probability-fill-danger"
                            : "probability-fill-safe"
                        }`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Model summary */}
          <div className="feature-summary">
            <div>
              <strong>
                {Object.keys(result.features).length}
              </strong>
              <span>Features extracted</span>
            </div>

            <div>
              <strong>10</strong>
              <span>SVD components</span>
            </div>

            <div>
              <strong>SVD + MLP</strong>
              <span>Detection model</span>
            </div>
          </div>

          {/* Extracted URL features */}
          <details className="feature-details">
            <summary>
              <span>View extracted URL features</span>
              <span className="feature-count">
                {Object.keys(result.features).length} features
              </span>
            </summary>

            <div className="feature-table-wrap">
              <table className="feature-table">
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>Value</th>
                  </tr>
                </thead>

                <tbody>
                  {Object.entries(result.features).map(
                    ([feature, value]) => (
                      <tr key={feature}>
                        <td>{feature.replaceAll("_", " ")}</td>
                        <td>
                          {typeof value === "number"
                            ? Number(value.toFixed(4)).toString()
                            : String(value)}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          </details>

          {/* Safety disclaimer */}
          <div className="scanner-disclaimer">
            <AlertTriangle size={17} />
            <p>
              This result is a machine-learning prediction, not a
              guarantee of website safety. Verify suspicious links
              independently before interacting with them.
            </p>
          </div>

          {result.model && (
            <p className="model-version">
              Model: {result.model}
            </p>
          )}
        </div>
      )}
    </section>
  );
}
