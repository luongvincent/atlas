import type { Metadata } from "next";

import { AuthProvider } from "@/components/AuthProvider";
import { Header } from "@/components/Header";

import "./globals.css";

export const metadata: Metadata = {
  title: "Earnings Call Explainer",
  description: "Plain-language earnings call explanations for regular consumers.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Header />
          <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
