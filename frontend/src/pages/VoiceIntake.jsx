import { useRef, useState } from 'react';
import FallbackBadge from '../components/FallbackBadge';
import { extractInfo, transcribeAudio } from '../api';

export default function VoiceIntake({ onComplete }) {
  const [text, setText] = useState('');
  const [transcript, setTranscript] = useState('');
  const [extracted, setExtracted] = useState(null);
  const [loading, setLoading] = useState(false);
  const [usedFallback, setUsedFallback] = useState(false);
  const [recording, setRecording] = useState(false);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);

  async function runPipeline(sourceText) {
    setLoading(true);
    setUsedFallback(false);
    const tRes = sourceText
      ? { ok: true, data: { text: sourceText, source: 'typed' }, usedFallback: false }
      : null;
    let finalTranscript = sourceText;
    if (!sourceText && chunksRef.current.length) {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
      const tr = await transcribeAudio(file);
      setUsedFallback((f) => f || tr.usedFallback);
      finalTranscript = tr.data?.text || '';
      setTranscript(finalTranscript);
    } else {
      setTranscript(finalTranscript);
    }

    const ex = await extractInfo(finalTranscript || text);
    setUsedFallback((f) => f || ex.usedFallback);
    setExtracted(ex.data);
    setLoading(false);
    onComplete?.({ transcript: finalTranscript || text, extracted: ex.data });
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        runPipeline('');
      };
      mediaRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      setUsedFallback(true);
      runPipeline(text || 'My rice has brown leaf spots');
    }
  }

  function stopRecording() {
    mediaRef.current?.stop();
    setRecording(false);
  }

  return (
    <section className="panel">
      <h2>1. Voice / text intake</h2>
      <p className="hint">Bangla or English — record, upload audio, or type symptoms.</p>
      <FallbackBadge show={usedFallback} />

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Example: আমার ধানক্ষেতে পাতায় বাদামি দাগ..."
        rows={4}
      />

      <div className="row">
        {!recording ? (
          <button type="button" onClick={startRecording}>
            Record voice
          </button>
        ) : (
          <button type="button" className="danger" onClick={stopRecording}>
            Stop & transcribe
          </button>
        )}
        <label className="file-btn">
          Upload audio
          <input
            type="file"
            accept="audio/*"
            hidden
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              setLoading(true);
              const tr = await transcribeAudio(file);
              setUsedFallback(tr.usedFallback);
              setTranscript(tr.data?.text || '');
              const ex = await extractInfo(tr.data?.text || '');
              setUsedFallback((f) => f || ex.usedFallback);
              setExtracted(ex.data);
              setLoading(false);
              onComplete?.({ transcript: tr.data?.text, extracted: ex.data });
            }}
          />
        </label>
        <button type="button" onClick={() => runPipeline(text)} disabled={loading}>
          Use typed text
        </button>
      </div>

      {loading && <p className="loading">Processing…</p>}
      {transcript && (
        <div className="card">
          <h3>Transcript</h3>
          <p>{transcript}</p>
        </div>
      )}
      {extracted && (
        <div className="card">
          <h3>Structured extraction</h3>
          <pre>{JSON.stringify(extracted, null, 2)}</pre>
        </div>
      )}
    </section>
  );
}
