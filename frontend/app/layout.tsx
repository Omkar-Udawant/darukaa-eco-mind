import "./globals.css";
import Link from "next/link";

export const metadata = { title: "Darukaa.Earth — Environmental Intelligence", description: "AI Environmental Scientist for biodiversity" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-emerald-50/50 text-slate-900 min-h-screen">
        <header className="border-b bg-white/80 backdrop-blur sticky top-0 z-10">
          <nav className="max-w-6xl mx-auto px-4 py-3 flex gap-4 text-sm font-medium">
            <span className="font-bold text-emerald-800 mr-4">🌍 Darukaa.Earth</span>
            {[
              ["/", "Dashboard"], ["/chat", "Chat"], ["/metrics", "Metrics"],
              ["/reasoning", "Reasoning"], ["/sources", "Sources"],
              ["/recommendations", "Recommendations"], ["/reports", "Reports"], ["/admin", "Admin"]
            ].map(([href, label]) => (
              <Link key={href} href={href} className="hover:text-emerald-700">{label}</Link>
            ))}
          </nav>
        </header>
        <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
