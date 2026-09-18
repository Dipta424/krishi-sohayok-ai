import { useEffect, useState } from 'react';
import FallbackBadge from '../components/FallbackBadge';
import { synthesizeSpeech } from '../api';

export default function HealthCard({ intake, diagnosis, treatment, market }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [ttsFallback, setTtsFallback] = useState(false);

  const summaryBn =
    'আপনার পরামর্শ: ' +
    (diagnosis?.disease_name || 'রোগ নির্ণয়') +
    '। ' +
    (treatment?.treatment_plan?.spraying_recommendation || 'স্থানীয় কৃষি কর্মকর্তার সাথে যোগাযোগ করুন।');

  useEffect(() => {
    let url;
    (async () => {
      const res = await synthesizeSpeech(summaryBn);
      setTtsFallback(res.usedFallback);
      if (res.blob) {
        url = URL.createObjectURL(res.blob);
        setAudioUrl(url);
      }
    })();
    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [summaryBn]);

  const plan = treatment?.treatment_plan;

  return (
    <section className="panel health-card" id="health-card-print">
      <div className="no-print row">
        <h2>5. Field Health Card</h2>
        <button type="button" onClick={() => window.print()}>
          Print / Save PDF
        </button>
      </div>
      <FallbackBadge show={ttsFallback} />

      <header className="print-header">
        <h1>Krishi Sohayok — Field Health Card</h1>
        <p>{new Date().toLocaleString('en-BD', { timeZone: 'Asia/Dhaka' })}</p>
      </header>

      {audioUrl && (
        <audio controls src={audioUrl} className="no-print">
          <track kind="captions" />
        </audio>
      )}

      <div className="card grid">
        <div>
          <h3>Farmer report</h3>
          <p>{intake?.transcript || '—'}</p>
          <pre className="compact">{JSON.stringify(intake?.extracted, null, 2)}</pre>
        </div>
        <div>
          <h3>Diagnosis</h3>
          <p>{diagnosis?.disease_name}</p>
          <p>Severity: {diagnosis?.severity}</p>
        </div>
        <div>
          <h3>Treatment</h3>
          <p>{plan?.organic_treatment}</p>
          <p>{plan?.chemical_treatment}</p>
          <p>PHI: {plan?.pre_harvest_interval_days} days</p>
        </div>
        <div>
          <h3>Market</h3>
          {market ? (
            <>
              <p>Fair: {market.fair_price_estimate} BDT/kg</p>
              <p>{market.recommended_window}</p>
            </>
          ) : (
            <p>—</p>
          )}
        </div>
      </div>
      <p className="disclaimer">
        Demo advisory only — confirm chemicals and dosages with your local SAAO before application.
      </p>
    </section>
  );
}
