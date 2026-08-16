'use client';

import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('AFIP render error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: '2rem',
            textAlign: 'center',
            fontFamily: 'var(--font-body)',
            color: 'var(--color-text)',
            background: 'var(--color-bg-light)',
          }}
        >
          <h3>Something went wrong.</h3>
          <p>Please refresh the page.</p>
        </div>
      );
    }
    return this.props.children;
  }
}
