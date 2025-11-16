import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SRE AI Agent - Team OPSC',
  description: 'Enterprise Reliability Engineering Dashboard with AI-powered insights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}
