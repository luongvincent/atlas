import type { Metadata } from "next";
import { Source_Serif_4 } from "next/font/google";

import { AuthProvider } from "@/components/AuthProvider";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

import "./globals.css";

const serif = Source_Serif_4({ subsets: ["latin"], variable: "--font-serif", display: "swap" });

export const metadata: Metadata = {
  title: "Atlas Capital - Stocks, plainly explained.",
  description: "Plain-language AI overviews of stocks and financial data for family and retirement planning.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={serif.variable}>
      <body className="flex min-h-screen flex-col">
        <AuthProvider>
          <Header />
          <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">{children}</main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}