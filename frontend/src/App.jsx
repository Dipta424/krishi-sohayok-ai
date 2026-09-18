import { useState } from 'react';
import DiseaseDetect from './pages/DiseaseDetect';
import HealthCard from './pages/HealthCard';
import MarketCheck from './pages/MarketCheck';
import TreatmentPlan from './pages/TreatmentPlan';
import VoiceIntake from './pages/VoiceIntake';
import './App.css';

function App() {
  const [intake, setIntake] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [treatment, setTreatment] = useState(null);
  const [market, setMarket] = useState(null);

  return (
    <div className="app">
      <header className="topbar">
        <h1>Krishi Sohayok</h1>
        <p>AI agro-advisory for Bangladesh smallholders</p>
      </header>
      <main>
        <VoiceIntake onComplete={setIntake} />
        <DiseaseDetect onComplete={setDiagnosis} />
        <TreatmentPlan intake={intake} diagnosis={diagnosis} onComplete={setTreatment} />
        <MarketCheck
          sessionId={treatment?.session_id}
          defaultCrop={intake?.extracted?.crop_type}
          onComplete={setMarket}
        />
        <HealthCard
          intake={intake}
          diagnosis={diagnosis}
          treatment={treatment}
          market={market}
        />
      </main>
    </div>
  );
}

export default App;
