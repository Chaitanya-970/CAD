'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Droplets, Map, Camera } from 'lucide-react';
import styles from './header.module.css';

const NAV = [
  { href: '/dashboard', label: 'Dashboard', icon: Map },
  { href: '/crop', label: 'Crop Assessment', icon: Camera },
];

export default function Header({ children }) {
  const pathname = usePathname();

  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <Droplets size={20} />
        <span>AFIP</span>
        <span className={styles.tagline}>Flood Intelligence</span>
      </div>

      <nav className={styles.nav}>
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={pathname === href ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink}
          >
            <Icon size={15} />
            {label}
          </Link>
        ))}
      </nav>

      <div className={styles.right}>{children}</div>
    </header>
  );
}
