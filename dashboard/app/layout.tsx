import type { Metadata } from "next";
import "./globals.css";
import { Shield, Activity, Lock, Settings, Menu } from "lucide-react";
import Sidebar from "../components/Sidebar";

export const metadata: Metadata = {
    title: "PhishShield AI | Cyber Command",
    description: "Advanced Real-time Phishing Detection",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className="bg-background text-white antialiased selection:bg-primary selection:text-black scanline">
                <div className="flex h-screen overflow-hidden">
                    {/* Sidebar */}
                    {/* Sidebar */}
                    <Sidebar />

                    {/* Main Content */}
                    <main className="flex-1 overflow-y-auto relative bg-[#05050a]">
                        <div className="relative z-10 p-8">
                            {children}
                        </div>
                    </main>
                </div>
            </body>
        </html>
    );
}
