'use client';

import { Wifi, WifiOff, Zap, CheckCircle2 } from 'lucide-react';
import styles from './survival.module.css';

export default function ModeBanner({ mode, queuedCount, justRestored }) {
  if (justRestored) {
    return (
      <div className={`${styles.banner} ${styles.restored}`}>
        <CheckCircle2 size={16} />
        Back online — {queuedCount === 0 ? 'queued messages sent' : `${queuedCount} messages still queued`}
      </div>
    );
  }

  if (mode === 'offline') {
    return (
      <div className={`${styles.banner} ${styles.offline}`}>
        <WifiOff size={16} />
        Offline — {queuedCount} Message{queuedCount === 1 ? '' : 's'} Queued
      </div>
    );
  }

  if (mode === 'low-bandwidth') {
    return (
      <div className={`${styles.banner} ${styles.lowBandwidth}`}>
        <Zap size={16} />
        Low-Bandwidth Mode — Map tiles disabled
      </div>
    );
  }

  return null;
}
