import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

const client = axios.create({ baseURL: API_BASE, timeout: 120000 });

function wrap(fn, label) {
  return async (...args) => {
    try {
      const result = await fn(...args);
      return { ok: true, data: result, usedFallback: false, label };
    } catch (err) {
      console.error(label, err);
      return {
        ok: false,
        error: err.message,
        usedFallback: true,
        label,
        data: null,
      };
    }
  };
}

export async function transcribeAudio(file) {
  const form = new FormData();
  form.append('file', file);
  try {
    const { data } = await client.post('/api/speech/transcribe', form);
    return {
      ok: true,
      data,
      usedFallback: Boolean(data.fallback),
    };
  } catch (err) {
    return {
      ok: false,
      usedFallback: true,
      data: {
        text: 'আমার ধানক্ষেতে পাতায় বাদামি দাগ (offline demo)',
        source: 'client_fallback',
        fallback: true,
      },
      error: err.message,
    };
  }
}

export async function extractInfo(transcript) {
  try {
    const { data } = await client.post('/api/extract/', { transcript });
    return { ok: true, data, usedFallback: Boolean(data.fallback) };
  } catch (err) {
    return {
      ok: false,
      usedFallback: true,
      data: {
        crop_type: 'rice',
        symptoms: transcript,
        fallback: true,
      },
      error: err.message,
    };
  }
}

export async function detectDisease(file) {
  const form = new FormData();
  form.append('file', file);
  try {
    const { data } = await client.post('/api/vision/detect', form);
    return { ok: true, data, usedFallback: Boolean(data.fallback) };
  } catch (err) {
    return {
      ok: false,
      usedFallback: true,
      data: {
        disease_name: 'Rice Blast (demo)',
        severity: 'moderate',
        fallback: true,
      },
      error: err.message,
    };
  }
}

export async function fetchTreatment(payload) {
  try {
    const { data } = await client.post('/api/treatment/', payload);
    return { ok: true, data, usedFallback: Boolean(data.treatment_plan?.fallback) };
  } catch (err) {
    return {
      ok: false,
      usedFallback: true,
      data: {
        session_id: null,
        weather: { fallback: true },
        treatment_plan: {
          organic_treatment: 'Neem oil spray (demo)',
          chemical_treatment: 'Consult SAAO',
          dosage: 'Label rates only',
          safety_instructions: 'PPE required',
          pre_harvest_interval_days: 21,
          spraying_recommendation: 'Morning spray if dry',
          fallback: true,
        },
      },
      error: err.message,
    };
  }
}

export async function analyzeMarket(crop, farmerPrice, sessionId) {
  try {
    const { data } = await client.post('/api/market/analyze', {
      crop,
      farmer_price: Number(farmerPrice),
      session_id: sessionId ?? undefined,
    });
    return { ok: true, data, usedFallback: Boolean(data.fallback) };
  } catch (err) {
    return {
      ok: false,
      usedFallback: true,
      data: {
        fair_price_estimate: 44,
        is_undercut: Number(farmerPrice) < 35,
        recommended_window: 'Demo cached market data',
        fallback: true,
      },
      error: err.message,
    };
  }
}

export async function synthesizeSpeech(text) {
  try {
    const res = await client.post('/api/tts/', { text }, { responseType: 'blob' });
    const fallback = res.headers['x-tts-fallback'] === 'True';
    return { ok: true, blob: res.data, usedFallback: fallback };
  } catch (err) {
    return { ok: false, usedFallback: true, blob: null, error: err.message };
  }
}

export const healthCheck = wrap(() => client.get('/health').then((r) => r.data), 'health');
