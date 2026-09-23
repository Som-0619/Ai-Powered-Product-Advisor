import type { Metadata } from "next";
import { Bricolage_Grotesque, DM_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "../components/Header";
import { ThemeProvider } from "../components/ThemeProvider";

const bricolage = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-heading" });
const dmSans = DM_Sans({ subsets: ["latin"], variable: "--font-body" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

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
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var stored = localStorage.getItem('product_advisor_theme');
                  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                  var theme = stored === 'light' || stored === 'dark' ? stored : (prefersDark ? 'dark' : 'light');
                  if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                    document.documentElement.classList.remove('light');
                  } else {
                    document.documentElement.classList.remove('dark');
                    document.documentElement.classList.add('light');
                  }
                  document.documentElement.setAttribute('data-theme', theme);
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body
        className={`${bricolage.variable} ${dmSans.variable} ${jetbrainsMono.variable} min-h-screen bg-background text-foreground flex flex-col font-sans antialiased`}
      >
        <ThemeProvider>
          <Header />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="border-t border-slate-200/80 dark:border-white/5 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
            Product Advisor • Multimodal Product Intelligence & Comparison
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
