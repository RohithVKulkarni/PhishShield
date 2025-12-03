"use client";

import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: "right" as const,
            labels: {
                color: "#9ca3af",
                font: {
                    family: "'JetBrains Mono', monospace",
                    size: 12,
                },
                usePointStyle: true,
                pointStyle: "circle",
            },
        },
    },
    cutout: "70%",
};

const data = {
    labels: ["Phishing", "Malware", "Suspicious", "Safe"],
    datasets: [
        {
            data: [12, 19, 3, 5],
            backgroundColor: [
                "#ff0055", // Red
                "#7000ff", // Purple
                "#ffb800", // Yellow
                "#00f2ff", // Cyan
            ],
            borderColor: "rgba(0,0,0,0)",
            borderWidth: 0,
        },
    ],
};

export default function VectorChart() {
    return <Doughnut data={data} options={options} />;
}
