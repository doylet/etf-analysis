import type { Metadata } from "next";
// import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/auth-context";
import { ThemeProvider } from "@/components/ui/theme-provider";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

// Temporarily disabled due to network issues during build
// TODO: Re-enable when network access is available or use local font files
// const geistSans = Geist({
//   variable: "--font-geist-sans",
//   subsets: ["latin"],
// });

// const geistMono = Geist_Mono({
//   variable: "--font-geist-mono",
//   subsets: ["latin"],
// });

export const metadata: Metadata = {
  title: "ETF Analysis Dashboard",
  description: "Modern portfolio analysis and optimization platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className="antialiased"
        suppressHydrationWarning={true}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
          storageKey="ui-theme"
          forcedTheme={undefined}
        >
          <AuthProvider>
            <div className="min-h-screen bg-background text-foreground">
              <Header />
              
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
              </main>
              
              <Footer />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
