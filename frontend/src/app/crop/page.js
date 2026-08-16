'use client';

import { useRef, useState } from 'react';
import { Camera, Sprout } from 'lucide-react';
import Header from '@/components/layout/Header';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { api } from '@/lib/api';
import styles from './crop.module.css';

const MAX_BYTES = 5 * 1024 * 1024; // R36 — compress to ≤5MB

/** Compress an image client-side (canvas) until it's under MAX_BYTES. */
function compressImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;
        let quality = 0.9;
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        const render = () => {
          canvas.width = width;
          canvas.height = height;
          ctx.clearRect(0, 0, width, height);
          ctx.drawImage(img, 0, 0, width, height);
        };

        const tryCompress = () => {
          render();
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error('Compression failed'));
                return;
              }
              if (blob.size <= MAX_BYTES || (quality <= 0.4 && width <= 640)) {
                resolve(blob);
                return;
              }
              if (quality > 0.4) {
                quality -= 0.15;
              } else {
                width = Math.round(width * 0.8);
                height = Math.round(height * 0.8);
              }
              tryCompress();
            },
            'image/jpeg',
            quality
          );
        };

        tryCompress();
      };
      img.onerror = reject;
      img.src = e.target.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export default function CropPage() {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const inputRef = useRef(null);

  const handleFile = async (selected) => {
    if (!selected) return;
    setError(null);
    setResult(null);
    setPreviewUrl(URL.createObjectURL(selected));

    try {
      const compressed = await compressImage(selected);
      setFile(compressed);
    } catch {
      setFile(selected); // fall back to original if compression fails
    }
  };

  const submit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image', file, 'crop.jpg');
      const res = await api.cropAssess(formData);
      setResult(res);
    } catch (e) {
      setError("We couldn't assess this image. Please retake in better lighting.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <Header />
      <ErrorBoundary>
        <div className={styles.content}>
          <div className={styles.container}>
            <h1 className={styles.title}>Crop Damage Assessment</h1>
            <p className={styles.subtitle}>
              Upload a photo of your flooded field to get an instant AI-driven damage estimate and
              recovery advisory, in English and Assamese.
            </p>

            <label className={styles.uploadCard}>
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                onChange={(e) => handleFile(e.target.files?.[0])}
              />
              {previewUrl ? (
                // eslint-disable-next-line @next/next/no-img-element -- local blob: URL preview, next/image doesn't support blob sources
                <img src={previewUrl} alt="Selected crop" className={styles.preview} />
              ) : (
                <Camera size={40} color="var(--color-primary)" />
              )}
              <div className={styles.uploadHint}>
                {previewUrl ? 'Tap to choose a different photo' : 'Tap to choose or take a photo of your flooded field'}
              </div>
            </label>

            <div className={styles.actions}>
              <button className="btn-primary" onClick={submit} disabled={!file || loading}>
                {loading ? 'Assessing…' : 'Assess Damage'}
              </button>
            </div>

            {loading && (
              <div className={styles.loading}>
                <div className={styles.spinner} />
                Model inference can take 10–30 seconds…
              </div>
            )}

            {error && <div className={styles.errorBox}>{error}</div>}

            {result && (
              <div className={styles.resultCard}>
                <div className={styles.resultHeader}>
                  <h3><Sprout size={16} style={{ verticalAlign: 'middle', marginRight: 6 }} />{result.crop_type || 'Assessment Result'}</h3>
                </div>

                <div className={styles.resultRow}>
                  <div className={styles.resultStat}>
                    <div className={styles.resultStatLabel}>Crop</div>
                    <div className={styles.resultStatValue} style={{ fontSize: '1.1rem' }}>{result.crop_type || '—'}</div>
                  </div>
                  <div className={styles.resultStat}>
                    <div className={styles.resultStatLabel}>Damage</div>
                    <div className={styles.resultStatValue}>{result.damage_pct != null ? `${result.damage_pct}%` : '—'}</div>
                  </div>
                </div>

                {result.advisory_en && (
                  <div className={styles.advisoryBlock}>
                    <div className={styles.advisoryLabel}>Recovery Advisory (English)</div>
                    <div className={styles.advisoryText}>{result.advisory_en}</div>
                  </div>
                )}

                {result.advisory_as && (
                  <div className={styles.advisoryBlock}>
                    <div className={styles.advisoryLabel}>অসমীয়া উপদেশ</div>
                    <div className={styles.advisoryText}>{result.advisory_as}</div>
                  </div>
                )}

                <div className={styles.modelBadge}>
                  ⚡ Assessed by: {result.model_used || 'Fine-tuned AI'}
                </div>
              </div>
            )}
          </div>
        </div>
      </ErrorBoundary>
    </div>
  );
}
