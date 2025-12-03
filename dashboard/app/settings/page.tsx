"use client";

import { useState } from "react";
import { Save, Shield, Bell, Database, Cpu, Lock } from "lucide-react";

export default function SettingsPage() {
    const [sensitivity, setSensitivity] = useState(0.85);
    const [useHeuristic, setUseHeuristic] = useState(true);
    const [useML, setUseML] = useState(true);
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        alert("Configuration saved successfully!");
        setSaving(false);
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <header>
                <h2 className="text-3xl font-display font-bold text-white mb-2 tracking-wide">SYSTEM CONFIGURATION</h2>
                <p className="text-gray-400 font-mono text-sm">ADJUST DETECTION PARAMETERS // MANAGE ALERTS</p>
            </header>

            <div className="grid gap-8">
                {/* Detection Settings */}
                <section className="cyber-card-cyan p-8">
                    <h3 className="text-xl font-display font-bold text-white mb-6 flex items-center gap-3 border-b border-white/5 pb-4">
                        <Cpu className="text-primary" size={24} />
                        DETECTION ENGINE
                    </h3>

                    <div className="space-y-8">
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-bold text-primary tracking-wider">AI SENSITIVITY THRESHOLD</label>
                                <span className="text-xs font-mono text-primary">{sensitivity}</span>
                            </div>
                            <input
                                type="range"
                                min="0.5"
                                max="0.99"
                                step="0.01"
                                value={sensitivity}
                                onChange={(e) => setSensitivity(parseFloat(e.target.value))}
                                className="w-full accent-primary h-2 bg-white/10 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="flex justify-between text-[10px] text-gray-500 mt-2 font-mono uppercase">
                                <span>Conservative (Low FP)</span>
                                <span>Aggressive (High Recall)</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-primary/30 transition-all group">
                                <div>
                                    <div className="text-white font-bold text-sm tracking-wide group-hover:text-primary transition-colors">HEURISTIC ANALYSIS</div>
                                    <div className="text-xs text-gray-500 font-mono mt-1">Lexical pattern matching</div>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={useHeuristic}
                                        onChange={(e) => setUseHeuristic(e.target.checked)}
                                    />
                                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary shadow-[0_0_10px_rgba(0,242,255,0.3)]"></div>
                                </label>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-primary/30 transition-all group">
                                <div>
                                    <div className="text-white font-bold text-sm tracking-wide group-hover:text-primary transition-colors">ML MODEL (XGBOOST)</div>
                                    <div className="text-xs text-gray-500 font-mono mt-1">Advanced scoring engine</div>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={useML}
                                        onChange={(e) => setUseML(e.target.checked)}
                                    />
                                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary shadow-[0_0_10px_rgba(0,242,255,0.3)]"></div>
                                </label>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Notifications */}
                <section className="cyber-card-red p-8 border-secondary/20">
                    <h3 className="text-xl font-display font-bold text-white mb-6 flex items-center gap-3 border-b border-white/5 pb-4">
                        <Bell className="text-secondary" size={24} />
                        ALERT PROTOCOLS
                    </h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-secondary/30 transition-all">
                            <span className="text-gray-300 font-medium text-sm">Email Alerts for High Risk Threats</span>
                            <input type="checkbox" className="accent-secondary w-5 h-5 bg-white/10 border-white/20 rounded cursor-pointer" />
                        </div>
                        <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-secondary/30 transition-all">
                            <span className="text-gray-300 font-medium text-sm">Browser Push Notifications</span>
                            <input type="checkbox" defaultChecked className="accent-secondary w-5 h-5 bg-white/10 border-white/20 rounded cursor-pointer" />
                        </div>
                    </div>
                </section>

                <div className="flex justify-end pt-4">
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center gap-2 px-8 py-4 bg-primary text-black font-bold rounded-lg hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(0,242,255,0.4)] hover:shadow-[0_0_30px_rgba(0,242,255,0.6)] tracking-widest text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Save size={20} />
                        {saving ? "SAVING..." : "SAVE CONFIGURATION"}
                    </button>
                </div>
            </div>
        </div>
    );
}
