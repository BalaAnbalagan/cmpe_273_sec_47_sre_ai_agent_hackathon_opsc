import { NextRequest, NextResponse } from "next/server";

const COOKIE_NAME = process.env.AUTH_COOKIE_NAME || "sre_auth";

export async function POST(req: NextRequest) {
    const res = NextResponse.json({ success: true });

    // Clear the cookie by setting it expired
    res.cookies.set(COOKIE_NAME, "", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 0,
    });

    return res;
}