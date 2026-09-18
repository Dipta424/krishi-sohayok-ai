import { useState } from 'react';
import FallbackBadge from '../components/FallbackBadge';
import { detectDisease } from '../api';

function compressImage(file, maxBytes = 900_000) {
  return new Promise((resolve) => {
    if (file.size <= maxBytes) {
      resolve(file);
      return;
    }
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      const canvas = document.createElement('canvas');
      let { width, height } = img;
      const scale = Math.min(1, Math.sqrt(maxBytes / file.size));
      canvas.width = Math.floor(width * scale);
      canvas.height = Math.floor(height * scale);
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(
        (blob) => {
          URL.revokeObjectURL(url);
          resolve(new File([blob], file.name, { type: 'image/jpeg' }));
        },
        'image/jpeg',
        0.75,
      );
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(file);
    };
    img.src = url;
  });
}

export default function DiseaseDetect({ onComplete }) {
  const [preview, setPreview] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [usedFallback, setUsedFallback] = useState(false);

  async function onFile(file) {
    if (!file) return;
    setLoading(true);
    const compressed = await compressImage(file);
    setPreview(URL.createObjectURL(compressed));
    const res = await detectDisease(compressed);
    setUsedFallback(res.usedFallback);
    setDiagnosis(res.data);
    setLoading(false);
    onComplete?.(res.data);
  }

  return (
    <section className="panel">
      <h2>2. Disease detection</h2>
      <p className="hint">Upload a leaf photo (&lt;1MB after compression).</p>
      <FallbackBadge show={usedFallback} />
      <label className="file-btn primary">
        Choose image
        <input type="file" accept="image/*" hidden onChange={(e) => onFile(e.target.files?.[0])} />
      </label>
      {loading && <p className="loading">Analyzing image…</p>}
      {preview && <img src={preview} alt="Crop preview" className="preview" />}
      {diagnosis && (
        <div className="card diagnosis">
          <h3>{diagnosis.disease_name}</h3>
          <p>
            Severity: <strong>{diagnosis.severity}</strong> · Confidence:{' '}
            {diagnosis.confidence ?? '—'}
          </p>
          <p>Pathogen: {diagnosis.possible_pathogen}</p>
        </div>
      )}
    </section>
  );
}
