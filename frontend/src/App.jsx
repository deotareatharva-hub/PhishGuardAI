import { useEffect, useState } from "react";

import {
  Activity,
  ArrowUpRight,
  Bell,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Globe,
  LockKeyhole,
  Radar,
  ScanSearch,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Target,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import Sidebar from "./components/Sidebar";
import StatCard from "./components/StatCard";
import Scanner from "./components/Scanner";
import "./App.css";

// --------------------------------------------------
// CONFIGURATION
// --------------------------------------------------

const API_BASE_URL = "http://127.0.0.1:8000";

const REFRESH_INTERVAL = 10000;

// --------------------------------------------------
// HELPER FUNCTIONS
// --------------------------------------------------

function formatDateTime(dateString) {
  if (!dateString) {
    return "Unknown";
  }

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  return date.toLocaleString();
}

function getPredictionColor(predictedClass) {
  return Number(predictedClass) === 0 ? "#f87171" : "#4ade80";
}

function getPredictionLabel(scan) {
  if (scan.prediction) {
    return scan.prediction;
  }

  return Number(scan.predicted_class) === 0
    ? "Phishing"
    : "Legitimate";
}

// --------------------------------------------------
// API HELPER
// --------------------------------------------------

async function fetchJSON(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

// --------------------------------------------------
// DASHBOARD PAGE
// --------------------------------------------------

function Dashboard({ onNavigate }) {
  const [statistics, setStatistics] = useState({
    total_scans: 0,
    phishing_detected: 0,
    legitimate_detected: 0,
  });

  const [recentScans, setRecentScans] = useState([]);

  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        const [stats, history] = await Promise.all([
          fetchJSON(`${API_BASE_URL}/api/statistics`),
          fetchJSON(`${API_BASE_URL}/api/history?limit=500`),
        ]);

        if (!active) {
          return;
        }

        setStatistics({
          total_scans: Number(stats.total_scans ?? 0),
          phishing_detected: Number(
            stats.phishing_detected ?? 0
          ),
          legitimate_detected: Number(
            stats.legitimate_detected ?? 0
          ),
        });

        setRecentScans(
          Array.isArray(history.scans) ? history.scans : []
        );

        setApiError("");
      } catch (error) {
        console.error(
          "Failed to load dashboard data:",
          error
        );

        if (active) {
          setApiError(
            "Unable to load live data. Check that the backend is running."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    const intervalId = setInterval(
      loadDashboard,
      REFRESH_INTERVAL
    );

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  // Build an hourly chart from saved scan timestamps.
  // Only the latest 500 records are loaded for this chart.
  const now = new Date();

  const chartData = Array.from({ length: 9 }, (_, index) => {
    const hour = new Date(now);

    hour.setMinutes(0, 0, 0);
    hour.setHours(hour.getHours() - (8 - index));

    const scansInHour = recentScans.filter((scan) => {
      const scannedAt = new Date(scan.scanned_at);

      if (Number.isNaN(scannedAt.getTime())) {
        return false;
      }

      return (
        scannedAt.getFullYear() === hour.getFullYear() &&
        scannedAt.getMonth() === hour.getMonth() &&
        scannedAt.getDate() === hour.getDate() &&
        scannedAt.getHours() === hour.getHours()
      );
    }).length;

    return {
      time: hour.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }),
      scans: scansInHour,
    };
  });

  const displayedScans = recentScans.slice(0, 5);

  return (
    <>
      {/* Welcome Banner */}

      <section className="welcome-banner">
        <div className="welcome-content">
          <div className="welcome-tag">
            <Sparkles size={14} />
            AI-POWERED SECURITY
          </div>

          <h2>
            Stay ahead of <span>digital threats.</span>
          </h2>

          <p>
            Analyze URLs with your machine-learning model and
            explore the features behind its predictions.
          </p>

          <button
            className="primary-button"
            onClick={() => onNavigate("URL Scanner")}
          >
            <ScanSearch size={17} />
            Scan a URL
            <ArrowUpRight size={16} />
          </button>
        </div>

        <div className="welcome-graphic">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />

          <div className="shield-glow">
            <ShieldCheck size={74} strokeWidth={1.15} />
          </div>

          <span className="orbit-dot dot-one" />
          <span className="orbit-dot dot-two" />
          <span className="orbit-dot dot-three" />
        </div>
      </section>

      {/* Dashboard Heading */}

      <div className="section-title-row">
        <div>
          <span className="eyebrow">OVERVIEW</span>
          <h2>Security Dashboard</h2>
        </div>

        <span className="live-badge">
          <span className="status-dot" />
          API-connected scanner
        </span>
      </div>

      {/* Live Statistics */}

      <section className="stats-grid">
        <StatCard
          title="Total Scans"
          value={
            loading
              ? "..."
              : statistics.total_scans.toLocaleString()
          }
          description="Total URLs scanned and saved"
          icon={Globe}
          accent="cyan"
        />

        <StatCard
          title="Phishing Detected"
          value={
            loading
              ? "..."
              : statistics.phishing_detected.toLocaleString()
          }
          description="Predicted phishing URLs"
          icon={ShieldAlert}
          accent="purple"
        />

        <StatCard
          title="Legitimate URLs"
          value={
            loading
              ? "..."
              : statistics.legitimate_detected.toLocaleString()
          }
          description="Predicted legitimate URLs"
          icon={ShieldCheck}
          accent="green"
        />

        <StatCard
          title="Model Accuracy"
          value="99.88%"
          description="Measured on the existing test set"
          icon={Target}
          accent="orange"
        />
      </section>

      {/* Dashboard Chart and Model Information */}

      <section className="dashboard-grid">
        <div className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <h3>Scan Activity</h3>
              <p>Saved scans over the last 9 hours</p>
            </div>

            <span className="chart-label">LIVE DATA</span>
          </div>

          <div className="chart-area">
            {loading ? (
              <div className="chart-empty-state">
                Loading scan activity...
              </div>
            ) : apiError ? (
              <div className="chart-empty-state">
                Scan activity is unavailable.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient
                      id="scanGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor="#22d3ee"
                        stopOpacity={0.3}
                      />

                      <stop
                        offset="95%"
                        stopColor="#22d3ee"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    stroke="#20283a"
                    strokeDasharray="4 4"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="time"
                    stroke="#78849a"
                    tickLine={false}
                    axisLine={false}
                    fontSize={11}
                  />

                  <YAxis
                    stroke="#78849a"
                    tickLine={false}
                    axisLine={false}
                    fontSize={11}
                    allowDecimals={false}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#101726",
                      border: "1px solid #26334a",
                      borderRadius: "10px",
                      color: "#e5e7eb",
                    }}
                    formatter={(value) => [
                      value,
                      "Scans",
                    ]}
                  />

                  <Area
                    type="monotone"
                    dataKey="scans"
                    stroke="#22d3ee"
                    strokeWidth={2.5}
                    fill="url(#scanGradient)"
                    connectNulls
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

          <p className="chart-disclaimer">
            Activity is calculated from saved scan timestamps.
            The chart uses the latest 500 records.
          </p>
        </div>

        {/* Model Status */}

        <div className="panel model-panel">
          <div className="panel-heading">
            <div>
              <h3>Model Status</h3>
              <p>Current inference pipeline</p>
            </div>

            <BrainCircuit
              size={21}
              className="muted-icon"
            />
          </div>

          <div className="model-status-card">
            <div className="model-status-icon">
              <Activity size={23} />
            </div>

            <div>
              <strong>SVD + MLP</strong>
              <p>14 selected input features</p>
            </div>

            <span className="status-pill">Loaded</span>
          </div>

          <div className="model-detail">
            <span>Dimensionality reduction</span>
            <strong>Truncated SVD</strong>
          </div>

          <div className="model-detail">
            <span>Hidden layers</span>
            <strong>64 → 32 neurons</strong>
          </div>

          <div className="model-detail">
            <span>Optimizer</span>
            <strong>Adam</strong>
          </div>

          <div className="model-detail">
            <span>API endpoint</span>
            <strong className="endpoint-text">
              POST /api/scan
            </strong>
          </div>
        </div>
      </section>

      {/* Recent Activity */}

      <section className="panel recent-panel">
        <div className="panel-heading">
          <div>
            <h3>Recent Activity</h3>
            <p>Latest saved URL predictions</p>
          </div>

          <button
            className="text-button"
            onClick={() => onNavigate("Scan History")}
          >
            View history <ArrowUpRight size={15} />
          </button>
        </div>

        {apiError && (
          <p role="alert" className="api-error-message">
            {apiError}
          </p>
        )}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>URL / DOMAIN</th>
                <th>TYPE</th>
                <th>STATUS</th>
                <th>TIME</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4}>
                    Loading recent scans...
                  </td>
                </tr>
              ) : apiError ? (
                <tr>
                  <td colSpan={4}>
                    Could not retrieve recent scans.
                  </td>
                </tr>
              ) : displayedScans.length === 0 ? (
                <tr>
                  <td colSpan={4}>
                    No saved scans yet. Scan a URL to get started.
                  </td>
                </tr>
              ) : (
                displayedScans.map((scan) => (
                  <tr key={scan.id}>
                    <td>
                      <div className="domain-cell">
                        <Globe size={17} />
                        <span>{scan.url}</span>
                      </div>
                    </td>

                    <td>URL scan</td>

                    <td>
                      <span
                        className="sample-badge"
                        style={{
                          color: getPredictionColor(
                            scan.predicted_class
                          ),
                        }}
                      >
                        {getPredictionLabel(scan)}
                      </span>
                    </td>

                    <td>
                      {formatDateTime(scan.scanned_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

// --------------------------------------------------
// MODEL ANALYTICS PAGE
// --------------------------------------------------

function AnalyticsPage() {
  return (
    <section className="page-content">
      <div className="section-title-row">
        <div>
          <span className="eyebrow">MACHINE LEARNING</span>

          <h2>Model Analytics</h2>

          <p className="page-description">
            Architecture and evaluation of the saved model.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Accuracy"
          value="99.88%"
          description="Test-set result"
          icon={Target}
        />

        <StatCard
          title="Precision"
          value="99.86%"
          description="Test-set result"
          icon={ShieldCheck}
          accent="purple"
        />

        <StatCard
          title="Recall"
          value="99.81%"
          description="Test-set result"
          icon={Radar}
          accent="green"
        />

        <StatCard
          title="F1-score"
          value="99.83%"
          description="Test-set result"
          icon={Activity}
          accent="orange"
        />
      </div>

      <div className="panel information-panel">
        <h3>Model Architecture</h3>

        <div className="architecture-flow">
          <div className="architecture-node">
            14 URL features
          </div>

          <ArrowUpRight size={20} />

          <div className="architecture-node">
            StandardScaler
          </div>

          <ArrowUpRight size={20} />

          <div className="architecture-node">
            Truncated SVD · 10
          </div>

          <ArrowUpRight size={20} />

          <div className="architecture-node">
            MLP · 64 → 32
          </div>
        </div>

        <p className="muted-paragraph">
          These metrics come from the existing test-set evaluation.
          They should not be interpreted as a guarantee of performance
          on previously unseen URLs.
        </p>
      </div>
    </section>
  );
}

// --------------------------------------------------
// AI INSIGHTS PAGE
// --------------------------------------------------

function InsightsPage() {
  const insights = [
    {
      icon: Globe,
      title: "URL structure",
      description:
        "Inspect URL length, path length and domain characteristics.",
    },
    {
      icon: LockKeyhole,
      title: "HTTPS indicator",
      description:
        "Check whether the URL uses HTTPS. HTTPS alone does not prove a site is trustworthy.",
    },
    {
      icon: ShieldAlert,
      title: "Suspicious file extensions",
      description:
        "Flag selected executable and archive extensions in URL paths.",
    },
    {
      icon: BrainCircuit,
      title: "Model prediction",
      description:
        "Review the model's class probabilities and extracted input features.",
    },
  ];

  return (
    <section className="page-content">
      <div className="section-title-row">
        <div>
          <span className="eyebrow">EXPLAINABILITY</span>

          <h2>AI Insights</h2>

          <p className="page-description">
            Understand the URL indicators used by the scanner.
          </p>
        </div>
      </div>

      <div className="insights-grid">
        {insights.map(
          ({ icon: Icon, title, description }) => (
            <article
              className="panel insight-card"
              key={title}
            >
              <div className="insight-icon">
                <Icon size={23} />
              </div>

              <h3>{title}</h3>

              <p>{description}</p>
            </article>
          )
        )}
      </div>
    </section>
  );
}

// --------------------------------------------------
// MODEL PERFORMANCE PAGE
// --------------------------------------------------

function PerformancePage() {
  const metrics = [
    ["Accuracy", "99.88%"],
    ["Precision", "99.86%"],
    ["Recall", "99.81%"],
    ["F1-score", "99.83%"],
    ["Test samples", "20,485"],
    ["Explained variance ratio", "98.07%"],
  ];

  const matrix = [
    [13241, 10],
    [14, 7220],
  ];

  return (
    <section className="page-content">
      <div className="section-title-row">
        <div>
          <span className="eyebrow">EVALUATION</span>

          <h2>Model Performance</h2>

          <p className="page-description">
            Metrics recorded during evaluation of the 14-feature model.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        {metrics.map(([label, value], index) => (
          <StatCard
            key={label}
            title={label}
            value={value}
            description="Saved evaluation results"
            icon={index % 2 === 0 ? Target : Activity}
            accent={
              ["cyan", "purple", "green", "orange"][
                index % 4
              ]
            }
          />
        ))}
      </div>

      <div className="panel information-panel">
        <h3>Confusion Matrix</h3>

        <p className="muted-paragraph">
          Rows represent actual classes; columns represent
          predicted classes.
        </p>

        <div className="matrix-wrap">
          <table className="matrix-table">
            <thead>
              <tr>
                <th>Actual / Predicted</th>
                <th>Class 0</th>
                <th>Class 1</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <th>Class 0</th>

                <td className="matrix-good">
                  {matrix[0][0]}
                </td>

                <td className="matrix-error">
                  {matrix[0][1]}
                </td>
              </tr>

              <tr>
                <th>Class 1</th>

                <td className="matrix-error">
                  {matrix[1][0]}
                </td>

                <td className="matrix-good">
                  {matrix[1][1]}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p className="muted-paragraph">
          Class 0 represents phishing URLs, while class 1 represents
          legitimate URLs. Rows represent actual classes and columns
          represent predicted classes.
        </p>
      </div>
    </section>
  );
}

// --------------------------------------------------
// SCAN HISTORY PAGE
// --------------------------------------------------

function HistoryPage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    let active = true;

    async function loadHistory() {
      try {
        const data = await fetchJSON(
          `${API_BASE_URL}/api/history?limit=500`
        );

        if (active) {
          setScans(
            Array.isArray(data.scans) ? data.scans : []
          );

          setError("");
        }
      } catch (err) {
        console.error(
          "Failed to load scan history:",
          err
        );

        if (active) {
          setError(
            "Could not load scan history. Please check the backend connection."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadHistory();

    const intervalId = setInterval(
      loadHistory,
      REFRESH_INTERVAL
    );

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  const filteredScans = scans.filter((scan) => {
    const matchesSearch = String(scan.url ?? "")
      .toLowerCase()
      .includes(searchTerm.toLowerCase().trim());

    const prediction = getPredictionLabel(scan);

    const matchesFilter =
      filter === "All" || prediction === filter;

    return matchesSearch && matchesFilter;
  });

  return (
    <section className="page-content">
      <div className="section-title-row">
        <div>
          <span className="eyebrow">SCAN RECORDS</span>

          <h2>Scan History</h2>

          <p className="page-description">
            Browse URL predictions saved in the SQLite database.
          </p>
        </div>
      </div>

      {/* History Summary */}

      <div className="stats-grid">
        <StatCard
          title="Saved Scans"
          value={loading ? "..." : scans.length.toLocaleString()}
          description="Records retrieved from the API"
          icon={Activity}
          accent="cyan"
        />

        <StatCard
          title="Phishing"
          value={
            loading
              ? "..."
              : scans
                  .filter(
                    (scan) =>
                      Number(scan.predicted_class) === 0
                  )
                  .length.toLocaleString()
          }
          description="Phishing predictions in loaded history"
          icon={ShieldAlert}
          accent="purple"
        />

        <StatCard
          title="Legitimate"
          value={
            loading
              ? "..."
              : scans
                  .filter(
                    (scan) =>
                      Number(scan.predicted_class) === 1
                  )
                  .length.toLocaleString()
          }
          description="Legitimate predictions in loaded history"
          icon={ShieldCheck}
          accent="green"
        />
      </div>

      {/* Search and Filter */}

      <div className="panel recent-panel">
        <div className="panel-heading">
          <div>
            <h3>All Scanned URLs</h3>

            <p>
              {loading
                ? "Loading records..."
                : `${filteredScans.length} matching records`}
            </p>
          </div>

          <Clock3 size={21} className="muted-icon" />
        </div>

        <div className="history-controls">
          <input
            type="search"
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(event.target.value)
            }
            placeholder="Search URLs..."
            aria-label="Search scan history by URL"
          />

          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            aria-label="Filter scan history by prediction"
          >
            <option value="All">All predictions</option>
            <option value="Phishing">Phishing</option>
            <option value="Legitimate">Legitimate</option>
          </select>
        </div>

        {error && (
          <p role="alert" className="api-error-message">
            {error}
          </p>
        )}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>URL / DOMAIN</th>
                <th>PREDICTION</th>
                <th>CONFIDENCE</th>
                <th>DATE / TIME</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5}>
                    Loading saved scan history...
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={5}>
                    History is temporarily unavailable.
                  </td>
                </tr>
              ) : filteredScans.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    {scans.length === 0
                      ? "No scans saved yet. Scan a URL to create your first record."
                      : "No records match your search or filter."}
                  </td>
                </tr>
              ) : (
                filteredScans.map((scan) => (
                  <tr key={scan.id}>
                    <td>{scan.id}</td>

                    <td>
                      <div className="domain-cell">
                        <Globe size={17} />
                        <span>{scan.url}</span>
                      </div>
                    </td>

                    <td>
                      <span
                        className="sample-badge"
                        style={{
                          color: getPredictionColor(
                            scan.predicted_class
                          ),
                        }}
                      >
                        {getPredictionLabel(scan)}
                      </span>
                    </td>

                    <td>
                      {(
                        Number(scan.confidence ?? 0) * 100
                      ).toFixed(2)}
                      %
                    </td>

                    <td>
                      {formatDateTime(scan.scanned_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <p className="chart-disclaimer">
          The history endpoint currently returns at most 500 records.
          Confidence is the model's probability for its predicted class,
          not a guarantee that the prediction is correct.
        </p>
      </div>
    </section>
  );
}

// --------------------------------------------------
// ABOUT PROJECT PAGE
// --------------------------------------------------

function AboutPage() {
  const concepts = [
    [
      "Multilayer Perceptron",
      "A neural network used for classification.",
    ],
    [
      "Backpropagation",
      "Used during neural-network training to adjust weights.",
    ],
    [
      "Adam optimizer",
      "The optimizer configured for the MLP.",
    ],
    [
      "PCA",
      "A dimensionality-reduction technique; a separate project experiment can demonstrate it.",
    ],
    [
      "SVD",
      "Used here to reduce the 14 scaled input features to 10 components.",
    ],
    [
      "Autoencoder",
      "A neural-network architecture that learns a compressed representation.",
    ],
  ];

  return (
    <section className="page-content">
      <div className="section-title-row">
        <div>
          <span className="eyebrow">PROJECT INFORMATION</span>

          <h2>About PhishGuard-AI</h2>

          <p className="page-description">
            An INN mini project exploring machine learning for URL analysis.
          </p>
        </div>
      </div>

      <div className="panel information-panel">
        <h3>Project Overview</h3>

        <p className="muted-paragraph">
          PhishGuard-AI extracts numerical characteristics from a URL
          and passes them through a saved StandardScaler, Truncated SVD
          transformation and MLP classifier. Scan results are stored
          in a local SQLite database for history and dashboard statistics.
        </p>

        <h3 className="subsection-heading">INN Concepts</h3>

        <div className="concept-list">
          {concepts.map(([title, description]) => (
            <div className="concept-row" key={title}>
              <div className="concept-check">
                <CheckCircle2 size={18} />
              </div>

              <div>
                <strong>{title}</strong>
                <p>{description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// --------------------------------------------------
// MAIN APPLICATION
// --------------------------------------------------

export default function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  function renderPage() {
    switch (activePage) {
      case "URL Scanner":
        return <Scanner />;

      case "Model Analytics":
        return <AnalyticsPage />;

      case "AI Insights":
        return <InsightsPage />;

      case "Performance":
        return <PerformancePage />;

      case "Scan History":
        return <HistoryPage />;

      case "About Project":
        return <AboutPage />;

      default:
        return <Dashboard onNavigate={setActivePage} />;
    }
  }

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />

      <main className="main-area">
        {/* Top Navigation */}

        <header className="topbar">
          <div>
            <div className="breadcrumb">
              Workspace <span>/</span> {activePage}
            </div>

            <p className="topbar-subtitle">
              Security intelligence and URL analysis
            </p>
          </div>

          <div className="topbar-actions">
            <div className="environment-badge">
              <span className="status-dot" />
              Local environment
            </div>

            <button
              className="icon-button"
              title="Notifications are not connected"
              aria-label="Notifications"
              type="button"
            >
              <Bell size={19} />
            </button>

            <div className="user-avatar">PG</div>
          </div>
        </header>

        {/* Main Page */}

        <div className="page-container">
          {renderPage()}

          <footer className="app-footer">
            <span>
              <Shield size={14} />
              PhishGuard-AI
            </span>

            <span>
              ML-based URL analysis · INN Mini Project
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}