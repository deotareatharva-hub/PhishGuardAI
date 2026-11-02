
import {
  LayoutDashboard,
  ScanSearch,
  ChartNoAxesCombined,
  BrainCircuit,
  Activity,
  History,
  Info,
  ShieldCheck,
} from "lucide-react";

const navigation = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "URL Scanner", icon: ScanSearch },
  { label: "Model Analytics", icon: ChartNoAxesCombined },
  { label: "AI Insights", icon: BrainCircuit },
  { label: "Performance", icon: Activity },
  { label: "Scan History", icon: History },
  { label: "About Project", icon: Info },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={24} />
        </div>

        <div>
          <h1>PhishGuard<span>-AI</span></h1>
          <p>CYBERSECURITY PLATFORM</p>
        </div>
      </div>

      <div className="nav-label">MAIN MENU</div>

      <nav className="nav-list">
        {navigation.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className={`nav-item ${
              activePage === label ? "active" : ""
            }`}
            onClick={() => onNavigate(label)}
          >
            <Icon size={19} strokeWidth={1.8} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="system-status">
          <span className="status-dot" />
          <div>
            <strong>System Online</strong>
            <p>AI detection engine</p>
          </div>
        </div>

        <div className="sidebar-footer">
          <span>PhishGuard-AI</span>
          <span>v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}
