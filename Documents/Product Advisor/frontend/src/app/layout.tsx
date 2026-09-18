import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "../components/Header";
import { ThemeProvider } from "../components/ThemeProvider";
import { CustomCursor } from "../components/CustomCursor";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Product Advisor | Multimodal Product Intelligence",
  description:
    "AI-powered multimodal product recommendation and intelligence platform for consumer electronics and electronic components.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} min-h-screen bg-background text-slate-900 dark:text-slate-100 flex flex-col font-sans antialiased selection:bg-blue-500/20 selection:text-blue-500`}
      >
        <ThemeProvider>
          <CustomCursor />
          <Header />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          <footer className="border-t border-slate-200/80 dark:border-white/5 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
            Product Advisor Platform • Local & AWS Portable Architecture
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
