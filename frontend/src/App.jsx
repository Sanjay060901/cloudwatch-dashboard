import React, { useEffect, useState, useRef } from "react";
import * as echarts from "echarts";
import axios from "axios";
import "./index.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading");

  const cpuChartRef = useRef(null);
  const lineChartRef = useRef(null);

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`${API}/metrics/latest`);
      setData(res.data);
      setStatus("ok");
    } catch (e) {
      setStatus("no-data");
    }
  };

  useEffect(() => {
    fetchMetrics();
    const id = setInterval(fetchMetrics, 5000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!data) return;

    const cpu = data.metrics?.ec2_cpu?.value;
    const rds = data.metrics?.rds_cpu?.value;
    const s3 = data.metrics?.s3_size?.value;

    if (!cpuChartRef.current) {
      cpuChartRef.current = echarts.init(document.getElementById("cpu-gauge"));
    }
    cpuChartRef.current.setOption({
      series: [
        {
          type: "gauge",
          progress: { show: true },
          detail: { valueAnimation: true, formatter: "{value}%" },
          data: [{ value: cpu ?? 0, name: "EC2 CPU" }],
        },
      ],
    });

    if (!lineChartRef.current) {
      lineChartRef.current = echarts.init(
        document.getElementById("line-chart")
      );
    }

    lineChartRef.current.setOption({
      tooltip: { trigger: "axis" },
      legend: { data: ["EC2 CPU", "RDS CPU", "S3 Size"] },
      xAxis: { type: "category", data: [data.updated_at] },
      yAxis: { type: "value" },
      series: [
        {
          name: "EC2 CPU",
          type: "line",
          data: [cpu ?? 0],
        },
        {
          name: "RDS CPU",
          type: "line",
          data: [rds ?? 0],
        },
        {
          name: "S3 Size",
          type: "line",
          data: [s3 ?? 0],
        },
      ],
    });
  }, [data]);

  return (
    <div className="container">
      <h1>CloudWatch Live Dashboard</h1>
      <p>Status: {status}</p>

      <div id="cpu-gauge" style={{ height: 250 }}></div>
      <div id="line-chart" style={{ height: 300 }}></div>
    </div>
  );
}
