import './globals.css';

export const metadata = {
  title: 'AFIP — Flood Intelligence',
  description: 'Assam Flood Intelligence Platform — 48-hour flood prediction, safe-zone recommendation, SMS/IVR alerting, and AI-powered crop damage assessment.',
  icons: {
    icon: '/favicon.svg',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
