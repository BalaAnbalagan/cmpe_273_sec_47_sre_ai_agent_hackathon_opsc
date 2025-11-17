"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function LoginPage() {
    const router = useRouter();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const res = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (res.ok) {
                // Cookie set by backend. Just redirect.
                router.push("/dashboard");
            } else {
                const data = await res.json().catch(() => ({}));
                setError(data.error || "Login failed");
            }
        } catch (err: any) {
            setError("Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center bg-muted">
            <Card className="w-full max-w-sm p-6 space-y-4">
                <h1 className="text-xl font-semibold text-center">
                    SRE Tier-0 Test Driver Login
                </h1>
                <form onSubmit={handleSubmit} className="space-y-3">
                    <div className="space-y-1">
                        <label className="text-sm font-medium">Username</label>
                        <Input
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            placeholder="ADMIN1"
                            required
                        />
                    </div>
                    <div className="space-y-1">
                        <label className="text-sm font-medium">Password</label>
                        <Input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            placeholder="•••••••"
                            required
                        />
                    </div>

                    {error && (
                        <p className="text-sm text-red-500">{error}</p>
                    )}

                    <Button
                        type="submit"
                        className="w-full"
                        disabled={loading}
                    >
                        {loading ? "Logging in..." : "Login"}
                    </Button>
                </form>
            </Card>
        </main>
    );
}
