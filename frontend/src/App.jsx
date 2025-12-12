import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import InstanceRow from "./components/InstanceRow";
import MetricsPanel from "./components/MetricsPanel";
import axios from "axios";

const BACKEND = import.meta.env.VITE_BACKEND_URL;

export default function App() {
  const [view, setView] = useState("instances");
  const [instances, setInstances] = useState([]);
  const [selected, setSelected] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const loadInstances = async () => {
    const res = await axios.get(`${BACKEND}/api/instances`);
    setInstances(res.data);
  };

  const loadMetrics = async () => {
    if (!selected) return;
    const res = await axios.get(`${BACKEND}/api/metrics/${selected}`);
    setMetrics(res.data);
  };
  

  useEffect(() => {
    loadInstances();
    const timer = setInterval(loadInstances, 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (selected) loadMetrics();
  }, [selected]);

  return (
    <>
      <Sidebar selected={view} setSelected={setView} />
      <div style={{ marginLeft: "260px", padding: "20px" }}>
        <h1 style={{ color: "#f5a623" }}>EC2 Dashboard</h1>
        {view === "instances" && (
          <div>
            <h2>Instances</h2>

            {instances.map((i) => (
              <InstanceRow key={i.InstanceId} instance={i} onSelect={setSelected} />
            ))}

            {instances.length === 0 && <p>No instances found.</p>}
          </div>
        )}

        {view === "metrics" && selected && metrics && (
          <MetricsPanel instanceId={selected} metrics={metrics} />
        )}

        {view === "metrics" && !selected && (
          <p>Select an instance from the left menu.</p>
        )}
      </div>
    </>
  );
}
