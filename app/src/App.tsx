import { useState, useCallback } from "react";
import type { MonteCarloResult } from "./simulation/engine";
import { monteCarlo } from "./simulation/engine";
import { Bracket } from "./components/Bracket";
import { StatsPanel } from "./components/StatsPanel";

function App() {
  const [state, setState] = useState<"idle" | "running" | "playing" | "done">("idle");
  const [result, setResult] = useState<MonteCarloResult | null>(null);
  const [simCount, setSimCount] = useState(5000);
  const [progress, setProgress] = useState(0);

  const handleStart = useCallback(() => {
    setState("running");
    setProgress(0);

    // Let the UI update before blocking with the computation
    requestAnimationFrame(() => {
      setTimeout(() => {
        const mc = monteCarlo(simCount);
        setResult(mc);
        setState("playing");
      }, 50);
    });
  }, [simCount]);

  function handleComplete() {
    setState("done");
  }

  function handleReplay() {
    setState("idle");
    setResult(null);
  }

  if (state === "idle") {
    return (
      <div className="cinema start-screen">
        <div className="start-content">
          <div className="start-icon">⚽</div>
          <h1>WORLD CUP 2026</h1>
          <p className="start-sub">MONTE CARLO SIMULATION</p>

          <div className="sim-config">
            <label className="sim-label">
              SIMULATIONS: <span className="sim-value">{simCount.toLocaleString()}</span>
            </label>
            <input
              type="range"
              min={100}
              max={20000}
              step={100}
              value={simCount}
              onChange={(e) => setSimCount(Number(e.target.value))}
              className="sim-slider"
            />
            <div className="sim-range">
              <span>100</span>
              <span>20,000</span>
            </div>
          </div>

          <button className="start-btn" onClick={handleStart}>
            SIMULATE
          </button>
          <p className="start-hint">48 teams · 12 groups · {simCount.toLocaleString()} simulations · Best bracket shown</p>
        </div>
      </div>
    );
  }

  if (state === "running") {
    return (
      <div className="cinema start-screen">
        <div className="start-content">
          <div className="start-icon spin">⚽</div>
          <h1>SIMULATING...</h1>
          <p className="start-sub">RUNNING {simCount.toLocaleString()} TOURNAMENTS</p>
          <div className="progress-bar">
            <div className="progress-fill" />
          </div>
        </div>
      </div>
    );
  }

  if (result && (state === "playing" || state === "done")) {
    return (
      <>
        <Bracket result={result.bestBracket} onComplete={handleComplete} />
        {state === "done" && (
          <>
            <StatsPanel result={result} />
            <button className="replay-btn" onClick={handleReplay}>
              ↻ SIMULATE AGAIN
            </button>
          </>
        )}
      </>
    );
  }

  return null;
}

export default App;
