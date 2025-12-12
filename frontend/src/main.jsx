import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import MetricChart from "./components/MetricChart";

let API_BASE = import.meta.env.VITE_BACKEND_URL;
if (!API_BASE) {
  API_BASE = `http://${window.location.hostname}:5000`;
}

console.log("Using backend:", API_BASE);

// COMPONENT: INSTANCE LIST
function Instances({ onSelect }) {
  const [instances, setInstances] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/instances`)
      .then(res => res.json())
      .then(data => setInstances(data.instances || []))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="content">
      <h2 className="section-title">Instances</h2>

      {instances.length === 0 ? (
        <p>No instances found.</p>
      ) : (
        <ul>
          {instances.map(inst => (
            <li
              key={inst.id}
              style={{ cursor: "pointer", marginBottom: "10px" }}
              onClick={() => onSelect(inst.id)}
            >
              <strong>{inst.id}</strong> — {inst.type} — {inst.state}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// COMPONENT: METRICS VIEW
function Metrics({ instanceId }) {
  const [metrics, setMetrics] = useState(null);

  const load = () => {
    if (!instanceId) return;
    fetch(`${API_BASE}/api/metrics/${instanceId}`)
      .then(res => res.json())
      .then(data => setMetrics(data));
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 30000); // refresh 30 sec
    return () => clearInterval(timer);
  }, [instanceId]);

  if (!instanceId) return <div className="content"><p>Select instance.</p></div>;
  if (!metrics) return <div className="content"><p>Loading...</p></div>;

  return (
    <div className="content">
      <h2 className="section-title">Metrics for {instanceId}</h2>

      <MetricChart title="CPU Utilization" datapoints={metrics.CPUUtilization} />
      <MetricChart title="Network In" datapoints={metrics.NetworkIn} />
      <MetricChart title="Network Out" datapoints={metrics.NetworkOut} />
      <MetricChart title="Disk Read Bytes" datapoints={metrics.DiskReadBytes} />
      <MetricChart title="Disk Write Bytes" datapoints={metrics.DiskWriteBytes} />
      <MetricChart title="Status Check Failed" datapoints={metrics.StatusCheckFailed} />

      <a
        href={`https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#metricsV2:graph=~();search=${instanceId}`}
        target="_blank"
        style={{ color: "#f2a900" }}
      >
        Open in CloudWatch →
      </a>
    </div>
  );
}

// MAIN APP
function App() {
  const [page, setPage] = useState("instances");
  const [selected, setSelected] = useState(null);

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <div className="sidebar-logo">
          {/* UPDATED LOGO PATH */}
          <img src="/digitide-logo.png" alt="Digitide" />
        </div>

        <h2 style={{ color: "#f2a900" }}>EC2 Dashboard</h2>

        <button onClick={() => setPage("instances")}>Instances</button>
        <button onClick={() => setPage("metrics")}>EC2 Metrics</button>
      </div>

      {page === "instances"
        ? <Instances onSelect={(id) => { setSelected(id); setPage("metrics"); }} />
        : <Metrics instanceId={selected} />}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
