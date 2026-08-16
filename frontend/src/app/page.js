import Link from 'next/link';
import { Droplets } from 'lucide-react';
import styles from './page.module.css';

const PILLARS = [
  {
    n: '01',
    title: 'Predict',
    text: '48-hour flood forecasting combines river levels and elevation data to flag villages before water rises.',
  },
  {
    n: '02',
    title: 'Alert',
    text: 'SMS and Assamese IVR voice calls reach every phone — smartphone or basic — the moment risk crosses a threshold.',
  },
  {
    n: '03',
    title: 'Protect',
    text: 'Dynamic safe-zone placement and post-flood crop advisory help communities recover faster.',
  },
];

export default function LandingPage() {
  return (
    <>
      <div className={styles.hero}>
        <div className={styles.heroNav}>
          <Droplets size={22} />
          AFIP
        </div>

        <div className={styles.heroMain}>
          <h1 className={styles.heroTitle}>
            Flood
            <span className={styles.heroTitleAccent}>Intelligence, before it floods</span>
          </h1>
          <p className={styles.heroSubtitle}>
            A proactive flood-intelligence platform for the Brahmaputra valley — predicting risk 48 hours
            ahead, delivering warnings through any signal condition, and protecting lives and livelihoods
            along the way.
          </p>
          <div className={styles.heroActions}>
            <Link href="/dashboard" className={styles.heroBtnPrimary}>
              Open Dashboard
            </Link>
            <Link href="/crop" className={styles.heroBtnOutline}>
              Crop Assessment
            </Link>
          </div>
        </div>
      </div>

      <div className={styles.pillars}>
        <div className={styles.pillarsGrid}>
          {PILLARS.map((p) => (
            <div key={p.n} className={styles.pillarCard}>
              <span className={styles.pillarNumber}>{p.n}</span>
              <h3 className={styles.pillarTitle}>{p.title}</h3>
              <p className={styles.pillarText}>{p.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.footer}>Assam Flood Intelligence Platform — Craft N Code 2026</div>
    </>
  );
}
