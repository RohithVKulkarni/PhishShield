"use client";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false,
        },
        tooltip: {
            mode: "index" as const,
            intersect: false,
            backgroundColor: "rgba(15, 17, 26, 0.9)",
            titleColor: "#fff",
            bodyColor: "#ccc",
            borderColor: "rgba(255, 255, 255, 0.1)",
            borderWidth: 1,
        },
    },
    scales: {
        x: {
            grid: {
                color: "rgba(255, 255, 255, 0.05)",
            },
            ticks: {
                color: "#6b7280",
            },
        },
        y: {
            grid: {
                color: "rgba(255, 255, 255, 0.05)",
            },
            ticks: {
                color: "#6b7280",
            },
        },
    },
    interaction: {
        mode: "nearest" as const,
        axis: "x" as const,
        intersect: false,
    },
};

export default function TrafficChart() {
    // Mock data for now, would come from API
    const labels = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"];

    const data = {
        labels,
        datasets: [
            {
                fill: true,
                label: "Safe Traffic",
                data: [65, 59, 80, 81, 56, 55, 40],
                borderColor: "#00f2ff",
                backgroundColor: "rgba(0, 242, 255, 0.1)",
                tension: 0.4,
            },
            {
                fill: true,
                label: "Threats",
                data: [28, 48, 40, 19, 86, 27, 90],
                borderColor: "#ff0055",
                backgroundColor: "rgba(255, 0, 85, 0.1)",
                tension: 0.4,
            },
        ],
    };

    return <Line options={options} data={data} />;
}
