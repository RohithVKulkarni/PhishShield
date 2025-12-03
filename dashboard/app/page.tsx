"use client";

import { Activity, ShieldAlert, Zap, Globe, CheckCircle, Shield } from "lucide-react";
import TrafficChart from "@/components/charts/TrafficChart";
import { useState, useEffect } from "react";

const StatCard = ({ title, value, subvalue, icon: Icon, color = "cyan" }: any) => {
    const isRed = color === "red";
    const borderColor = isRed ? "border-secondary/30" : "border-primary/30";
    const textColor = isRed ? "text-secondary" : "text-primary";
    const glowClass = isRed ? "cyber-card-red" : "cyber-card-cyan";
    const barColor = isRed ? "bg-secondary" : "bg-primary";

    return (
        <div className={`${glowClass} p-6 relative overflow-hidden group`}>
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-lg bg-white/5 ${borderColor} border`}>
                    <Icon size={24} className={textColor} />
                </div>
                <span className={`text-xs font-mono ${textColor}`}>{subvalue}</span>
            </div>

            <div className="space-y-1">
                <div className="text-gray-400 text-[10px] uppercase tracking-widest font-display">{title}</div>
                <div className="text-3xl font-display font-bold text-white tracking-wide">{value}</div>
            </div>

            {/* Progress Bar Decoration */}
            <div className="mt-4 h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <div className={`h-full ${barColor} w-3/4 shadow-[0_0_10px_currentColor]`}></div>
            </div>
        </div>
    );
};

export default function Home() {
    const [time, setTime] = useState<string | null>(null);
    const [recentScans, setRecentScans] = useState<any[]>([]);
    const [stats, setStats] = useState({
        total_scans: 0,
        threats_neutralized: 0,
        active_nodes: 49,
        latency: 23
    });

    useEffect(() => {
        setTime(new Date().toLocaleTimeString());
        const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);

        // Poll for recent scans and stats
        const fetchData = async () => {
            try {
                const [resScans, resStats] = await Promise.all([
                    fetch('http://localhost:8000/api/v1/score/recent'),
                    fetch('http://localhost:8000/api/v1/stats')
                ]);

                if (resScans.ok) {
                    const data = await resScans.json();
                    setRecentScans(data);
                }
                if (resStats.ok) {
                    const data = await resStats.json();
                    setStats(data);
                }
            } catch (e) {
                console.error("Failed to fetch data", e);
            }
        };

        fetchData(); // Initial fetch
        const dataTimer = setInterval(fetchData, 2000); // Poll every 2s

        return () => {
            clearInterval(timer);
            clearInterval(dataTimer);
        };
    }, []);

    return (
        <div className="space-y-8 max-w-[1600px] mx-auto">
            {/* Header Section from Screenshot */}
            <header className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <h1 className="font-display font-bold text-2xl tracking-wider text-white">PHISH<span className="text-primary">SHIELD</span></h1>
                </div>
                <div className="flex items-center gap-6">
                    <div className="font-mono text-gray-400 text-sm flex items-center gap-2">
                        <Activity size={16} className="text-primary" />
                        {time}
                    </div>
                    <div className="px-4 py-1.5 rounded bg-primary/10 border border-primary/30 text-primary text-xs font-bold tracking-wider flex items-center gap-2 shadow-[0_0_10px_rgba(0,242,255,0.2)]">
                        <div className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_5px_#00f2ff]"></div>
                        SYSTEM ONLINE
                    </div>
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="TOTAL SCANS"
                    value={stats.total_scans.toLocaleString()}
                    subvalue="+12%"
                    icon={Activity}
                    color="cyan"
                />
                <StatCard
                    title="THREATS NEUTRALIZED"
                    value={stats.threats_neutralized.toLocaleString()}
                    subvalue="+8%"
                    icon={ShieldAlert}
                    color="red"
                />
                <StatCard
                    title="ACTIVE NODES"
                    value={stats.active_nodes}
                    subvalue="-2%"
                    icon={Zap}
                    color="cyan"
                />
                <StatCard
                    title="LATENCY (MS)"
                    value={stats.latency}
                    subvalue="-5%"
                    icon={Activity}
                    color="cyan"
                />
            </div>

            {/* Main Chart Section */}
            <div className="cyber-card-cyan p-1 border-primary/20">
                <div className="bg-surface/50 p-6 rounded-xl h-[400px] relative">
                    <div className="absolute top-6 left-6 z-10">
                        <h3 className="text-primary font-display text-sm tracking-widest uppercase mb-1 font-bold">REAL-TIME TRAFFIC ANALYSIS</h3>
                    </div>
                    <div className="w-full h-full pt-8">
                        <TrafficChart />
                    </div>
                </div>
            </div>

            {/* Live Intercepts List */}
            <div className="cyber-card-cyan p-6 border-primary/20">
                <h3 className="text-primary font-display text-sm tracking-widest uppercase mb-6 border-l-2 border-primary pl-3">
                    Live URL Intercepts
                </h3>
                <div className="space-y-3">
                    {recentScans.length === 0 ? (
                        <div className="text-gray-500 text-center py-4 font-mono text-sm">WAITING FOR TRAFFIC...</div>
                    ) : (
                        recentScans.slice(0, 5).map((item: any, i: number) => (
                            <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/5 hover:border-primary/30 transition-all group">
                                <div className="flex items-center gap-4">
                                    {item.status === "PHISHING" ? (
                                        <ShieldAlert className="text-secondary" size={20} />
                                    ) : (
                                        <CheckCircle className="text-success" size={20} />
                                    )}
                                    <span className="font-mono text-sm text-gray-300 group-hover:text-white tracking-wide truncate max-w-[300px]">{item.url}</span>
                                </div>
                                <div className="flex items-center gap-6">
                                    <span className="font-mono text-xs text-gray-500">{item.time}</span>
                                    <span className={`px-3 py-1 rounded text-[10px] font-bold tracking-wider w-24 text-center ${item.status === "PHISHING"
                                        ? "bg-secondary/20 text-secondary border border-secondary/30"
                                        : "bg-success/20 text-success border border-success/30"
                                        }`}>
                                        {item.status}
                                    </span>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
