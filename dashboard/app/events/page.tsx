"use client";

import { useState, useEffect } from "react";
import { Search, Filter, AlertTriangle, CheckCircle, ShieldAlert } from "lucide-react";

export default function EventsPage() {
    const [events, setEvents] = useState<any[]>([]);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/v1/score/recent');
                if (res.ok) {
                    const data = await res.json();
                    setEvents(data);
                }
            } catch (e) {
                console.error("Failed to fetch events", e);
            }
        };

        fetchEvents();
        const interval = setInterval(fetchEvents, 5000);
        return () => clearInterval(interval);
    }, []);

    const filteredEvents = events.filter(event =>
        event.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.status.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="space-y-6 max-w-[1600px] mx-auto">
            <header className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl font-display font-bold text-white mb-2 tracking-wide">SECURITY EVENTS</h2>
                    <p className="text-gray-400 font-mono text-sm">AUDIT LOG // SYSTEM ACTIONS</p>
                </div>
            </header>

            {/* Filters */}
            <div className="cyber-card-cyan p-4 flex gap-4 items-center">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-primary" size={20} />
                    <input
                        type="text"
                        placeholder="SEARCH THREAT LOGS..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-black/40 border border-primary/20 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-primary/50 font-mono text-sm placeholder:text-gray-600"
                    />
                </div>
                <button className="flex items-center gap-2 px-6 py-2 bg-primary/10 border border-primary/30 rounded-lg text-primary hover:bg-primary/20 transition-colors font-bold tracking-wider text-sm">
                    <Filter size={16} />
                    FILTER
                </button>
            </div>

            {/* Table */}
            <div className="cyber-card-cyan overflow-hidden p-0">
                <table className="w-full text-left">
                    <thead className="bg-white/5 text-primary text-xs uppercase tracking-widest font-display">
                        <tr>
                            <th className="p-6 font-bold">Status</th>
                            <th className="p-6 font-bold">URL</th>
                            <th className="p-6 font-bold">Type</th>
                            <th className="p-6 font-bold">Threat Score</th>
                            <th className="p-6 font-bold">Time</th>
                            <th className="p-6 font-bold">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {filteredEvents.map((event, index) => (
                            <tr key={index} className="hover:bg-white/5 transition-colors group">
                                <td className="p-6">
                                    {event.status === "PHISHING" && <ShieldAlert className="text-secondary drop-shadow-[0_0_5px_rgba(255,0,85,0.5)]" size={24} />}
                                    {event.status === "SAFE" && <CheckCircle className="text-success drop-shadow-[0_0_5px_rgba(0,255,157,0.5)]" size={24} />}
                                    {event.status === "warning" && <AlertTriangle className="text-warning" size={24} />}
                                </td>
                                <td className="p-6 font-mono text-sm text-gray-300 group-hover:text-white truncate max-w-md tracking-wide">
                                    {event.url}
                                </td>
                                <td className="p-6">
                                    <span className={`px-3 py-1 rounded text-[10px] font-bold tracking-wider border ${event.status === "PHISHING" ? "bg-secondary/10 text-secondary border-secondary/30" :
                                        event.status === "SAFE" ? "bg-success/10 text-success border-success/30" :
                                            "bg-warning/10 text-warning border-warning/30"
                                        }`}>
                                        {event.status}
                                    </span>
                                </td>
                                <td className="p-6 font-mono text-sm">
                                    <div className="w-full bg-white/10 rounded-full h-2 w-32 overflow-hidden">
                                        <div
                                            className={`h-full ${event.score > 0.8 ? "bg-secondary shadow-[0_0_10px_#ff0055]" : event.score > 0.4 ? "bg-warning" : "bg-success shadow-[0_0_10px_#00ff9d]"}`}
                                            style={{ width: `${event.score * 100}%` }}
                                        ></div>
                                    </div>
                                </td>
                                <td className="p-6 text-sm text-gray-500 font-mono">{event.time}</td>
                                <td className="p-6">
                                    <button className="px-4 py-2 rounded bg-primary/10 text-primary border border-primary/30 text-xs font-bold hover:bg-primary/20 transition-all">
                                        REVIEW
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
