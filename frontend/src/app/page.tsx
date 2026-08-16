import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ padding: "2rem", fontFamily: "var(--font-geist-sans)" }}>
      <h1>AFIP — Flood Intelligence</h1>
      <p>Assam Flood Intelligence Platform</p>
      
      <div style={{ marginTop: "2rem" }}>
        <Link href="/dashboard" style={{ marginRight: "1rem", color: "blue" }}>Go to Dashboard</Link>
        <Link href="/crop" style={{ color: "blue" }}>Go to Crop Assessment</Link>
      </div>
    </main>
  );
}
