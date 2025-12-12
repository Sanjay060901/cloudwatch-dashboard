import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend
} from "chart.js";

import "chartjs-adapter-date-fns";

Chart.register(LineElement, PointElement, LinearScale, TimeScale, Tooltip, Legend);

export default function MetricChart({ title, datapoints }) {
  if (!datapoints || datapoints.length === 0) {
    return <p>No data available...</p>;
  }

  const sorted = datapoints.sort(
    (a, b) => new Date(a.Timestamp) - new Date(b.Timestamp)
  );

  const data = {
    labels: sorted.map((p) => new Date(p.Timestamp)),
    datasets: [
      {
        label: title,
        data: sorted.map((p) => p.Average || p.Sum || 0),
        borderColor: "#f2a900",
        tension: 0.3,
      }
    ],
  };

  const options = {
    responsive: true,
    scales: {
      x: { type: "time", time: { unit: "minute" }, ticks: { color: "white" } },
      y: { ticks: { color: "white" } }
    },
    plugins: {
      legend: { labels: { color: "white" } }
    }
  };

  return (
    <div style={{ marginBottom: "30px" }}>
      <h3 style={{ color: "#f2a900" }}>{title}</h3>
      <Line data={data} options={options} />
    </div>
  );
}
