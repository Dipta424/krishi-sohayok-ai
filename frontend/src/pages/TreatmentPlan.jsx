import { useEffect, useState } from 'react';
import FallbackBadge from '../components/FallbackBadge';
import { fetchTreatment } from '../api';

export default function TreatmentPlan({ intake, diagnosis, onComplete }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [usedFallback, setUsedFallback] = useState(false);

  useEffect(() => {
    if (!intake?.extracted || !diagnosis) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      const res = await fetchTreatment({
        extracted: intake.extracted,
        diagnosis,
        transcript: intake.transcript,
      });
      if (cancelled) return;
      setUsedFallback(res.usedFallback);
      setResult(res.data);
      setLoading(false);
      onComplete?.(res.data);
    })();
    return () => {
      cancelled = true;
    };
  }, [intake, diagnosis, onComplete]);

  if (!intake?.extracted || !diagnosis) {
    return (
      <section className="panel muted">
        <h2>3. Treatment plan</h2>
        <p>Complete voice intake and disease detection first.</p>
      </section>
    );
  }

  const plan = result?.treatment_plan;
  const weather = result?.weather;

  return (
    <section className="panel">
      <h2>3. Treatment plan</h2>
      <FallbackBadge show={usedFallback} />
      {loading && <p className="loading">Generating advisory…</p>}
      {weather && (
        <div className="card small">
          Weather: {weather.temperature_c}°C, humidity {weather.humidity_percent}% —{' '}
          {weather.rain_within_6h ? 'Rain expected — postpone spray' : 'Favorable for scheduled spray'}
        </div>
      )}
      {plan && (
        <div className="card">
          <p>{plan.disease_explanation}</p>
          <p>
            <strong>Organic:</strong> {plan.organic_treatment}
          </p>
          <p>
            <strong>Chemical:</strong> {plan.chemical_treatment}
          </p>
          <p>
            <strong>Dosage:</strong> {plan.dosage}
          </p>
          <p>
            <strong>Safety:</strong> {plan.safety_instructions}
          </p>
          <p>
            <strong>Pre-harvest interval:</strong> {plan.pre_harvest_interval_days} days
          </p>
          <p>
            <strong>Spray timing:</strong> {plan.spraying_recommendation}
          </p>
        </div>
      )}
    </section>
  );
}
