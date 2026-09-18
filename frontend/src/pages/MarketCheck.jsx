import { useState } from 'react';
import FallbackBadge from '../components/FallbackBadge';
import { analyzeMarket } from '../api';

export default function MarketCheck({ sessionId, defaultCrop, onComplete }) {
  const [crop, setCrop] = useState(defaultCrop || 'rice');
  const [price, setPrice] = useState('');
  const [result, setResult] = useState(null);
  const [usedFallback, setUsedFallback] = useState(false);
  const [loading, setLoading] = useState(false);

  async function analyze() {
    setLoading(true);
    const res = await analyzeMarket(crop, price || 0, sessionId);
    setUsedFallback(res.usedFallback);
    setResult(res.data);
    setLoading(false);
    onComplete?.(res.data);
  }

  return (
    <section className="panel">
      <h2>4. Market check</h2>
      <FallbackBadge show={usedFallback} />
      <div className="row">
        <select value={crop} onChange={(e) => setCrop(e.target.value)}>
          <option value="rice">Rice</option>
          <option value="potato">Potato</option>
          <option value="tomato">Tomato</option>
        </select>
        <input
          type="number"
          placeholder="Your price (BDT/kg)"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />
        <button type="button" onClick={analyze} disabled={loading}>
          Analyze
        </button>
      </div>
      {result?.status === 'ok' && (
        <div className={`card ${result.is_undercut ? 'warn' : ''}`}>
          <p>Fair estimate: {result.fair_price_estimate} BDT/kg</p>
          <p>Z-score: {result.z_score}</p>
          <p>{result.is_undercut ? '⚠ Below market — possible undercut' : '✓ Price in normal range'}</p>
          <p>{result.recommended_window}</p>
        </div>
      )}
    </section>
  );
}
