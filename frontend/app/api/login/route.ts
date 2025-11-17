import { NextRequest, NextResponse } from "next/server";

const USERNAME = process.env.ADMIN_USERNAME;
const PASSWORD = process.env.ADMIN_PASSWORD;
const COOKIE_NAME = process.env.AUTH_COOKIE_NAME || "sre_auth";

export async function POST(req: NextRequest) {
    const { username, password } = await req.json();

    if (!USERNAME || !PASSWORD) {
        return NextResponse.json(
            { error: "Server auth not configured" },
            { status: 500 }
        );
    }

    if (username === USERNAME && password === PASSWORD) {
        const res = NextResponse.json(
            { success: true },
            { status: 200 }
        );

        // Very simple cookie: just “true” to mean logged in
        res.cookies.set(COOKIE_NAME, "true", {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            path: "/",
            maxAge: 60 * 60 * 8, // 8 hours
        });

        return res;
    }

    return NextResponse.json(
        { error: "Invalid credentials" },
        { status: 401 }
    );
}