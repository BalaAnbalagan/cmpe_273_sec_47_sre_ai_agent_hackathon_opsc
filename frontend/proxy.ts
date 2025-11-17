import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const COOKIE_NAME = process.env.AUTH_COOKIE_NAME || "sre_auth";

export function proxy(req: NextRequest) {
    const { pathname } = req.nextUrl;

    // Public routes
    if (
        pathname === "/login" ||
        pathname.startsWith("/api/login") ||
        pathname.startsWith("/_next") ||
        pathname.startsWith("/favicon") ||
        pathname === "/"
    ) {
        return NextResponse.next();
    }

    // For all other routes we want to protect (e.g. /dashboard, /sre, etc.)
    const authCookie = req.cookies.get(COOKIE_NAME);

    if (!authCookie || authCookie.value !== "true") {
        const loginUrl = new URL("/login", req.url);
        return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
}

// Only run middleware on specific paths (optional but recommended)
export const config = {
    matcher: ["/dashboard/:path*", "/sre/:path*", "/((?!api|_next|favicon.ico).*)"],
};