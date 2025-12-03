"use client";

import { Shield, Activity, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
    const pathname = usePathname();

    const isActive = (path: string) => pathname === path;

    return (
        <aside className="w-64 bg-[#0a0a12] border-r border-white/5 hidden md:flex flex-col z-20">
            <div className="p-6 flex items-center gap-3 border-b border-white/5">
                <div className="relative">
                    <Shield className="w-8 h-8 text-primary animate-pulse-slow" />
                    <div className="absolute inset-0 bg-primary/20 blur-lg rounded-full"></div>
                </div>
                <div>
                    <h1 className="font-display font-bold text-xl tracking-wider text-white">PHISH<span className="text-primary">SHIELD</span></h1>
                </div>
            </div>

            <nav className="flex-1 px-4 space-y-2 mt-6">
                <Link
                    href="/"
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all group ${isActive("/")
                            ? "bg-primary/5 text-primary border border-primary/20 shadow-[0_0_15px_rgba(0,242,255,0.1)]"
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        }`}
                >
                    <Activity size={20} className={isActive("/") ? "" : "group-hover:text-primary transition-colors"} />
                    <span className="font-medium tracking-wide text-sm">LIVE MONITOR</span>
                </Link>

                <Link
                    href="/events"
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all group ${isActive("/events")
                            ? "bg-primary/5 text-primary border border-primary/20 shadow-[0_0_15px_rgba(0,242,255,0.1)]"
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        }`}
                >
                    <Shield size={20} className={isActive("/events") ? "" : "group-hover:text-primary transition-colors"} />
                    <span className="font-medium tracking-wide text-sm">EVENTS LOG</span>
                </Link>

                <Link
                    href="/settings"
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all group ${isActive("/settings")
                            ? "bg-primary/5 text-primary border border-primary/20 shadow-[0_0_15px_rgba(0,242,255,0.1)]"
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        }`}
                >
                    <Settings size={20} className={isActive("/settings") ? "" : "group-hover:text-primary transition-colors"} />
                    <span className="font-medium tracking-wide text-sm">SYSTEM CONFIG</span>
                </Link>
            </nav>

            <div className="p-4">
                <div className="p-4 rounded-xl bg-gradient-to-br from-primary/10 to-transparent border border-primary/20">
                    <div className="text-xs text-primary font-mono mb-2">STATUS</div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>
                        <span className="text-sm font-bold text-white">OPERATIONAL</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
