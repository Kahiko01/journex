import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/auth/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import SimpleNav from '@/components/layout/SimpleNav';
import FastAIChat from '@/components/ai/FastAIChat';
import AnonymousTracker from '@/components/tracking/AnonymousTracker';

const inter = Inter({ subsets: ['latin'] });

export const viewport: Viewport = {
  themeColor: '#3B82F6',
  width: 'device-width',
  initialScale: 1,
};

export const metadata: Metadata = {
  title: 'Journex - Trading Journal',
  description: 'Professional trading journal platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ThemeProvider>
            <SimpleNav />
            <main className="min-h-screen bg-gray-900 pt-16">
              <AnonymousTracker>
                {children}
              </AnonymousTracker>
            </main>
            <FastAIChat />
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
