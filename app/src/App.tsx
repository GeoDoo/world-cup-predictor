import { useState, useCallback, useRef, useEffect } from "react";
import type { TournamentResult } from "./simulation/engine";
import type { MCWorkerMessage } from "./simulation/mc-worker";
import type { LiveOdds } from "./data/odds-api";
import { fetchLiveOdds } from "./data/odds-api";
import { Bracket } from "./components/Bracket";
import { LiveStats } from "./components/LiveStats";

type AppState = "idle" | "simulating" | "converged" | "playing";

interface MCState {
  completed: number;
  total: number;
  winCounts: Record<string, number>;
  finalCounts: Record<string, number>;
  semiCounts: Record<string, number>;
  qfCounts: Record<string, number>;
  bestBracket: TournamentResult | null;
}

function App() {
  const [state, setState] = useState<AppState>("idle");
  const [simCount, setSimCount] = useState(5000);
  const [liveOdds, setLiveOdds] = useState<Record<string, LiveOdds>>({});
  const [mc, setMC] = useState<MCState>({
    completed: 0, total: 0,
    winCounts: {}, finalCounts: {}, semiCounts: {}, qfCounts: {},
    bestBracket: null,
  });
  const workerRef = useRef<Worker | null>(null);

  useEffect(() => {
    fetchLiveOdds()
      .then(setLiveOdds)
      .catch(() => {});
  }, []);

  const handleStart = useCallback(() => {
    setState("simulating");
    setMC({ completed: 0, total: simCount, winCounts: {}, finalCounts: {}, semiCounts: {}, qfCounts: {}, bestBracket: null });

    const worker = new Worker(
      new URL("./simulation/mc-worker.ts", import.meta.url),
      { type: "module" }
    );
    workerRef.current = worker;

    worker.onmessage = (e: MessageEvent<MCWorkerMessage>) => {
      const msg = e.data;
      setMC({
        completed: msg.completed,
        total: msg.total,
        winCounts: msg.winCounts,
        finalCounts: msg.finalCounts,
        semiCounts: msg.semiCounts,
        qfCounts: msg.qfCounts,
        bestBracket: msg.bestBracket,
      });

      if (msg.type === "done") {
        setState("converged");
        worker.terminate();
        workerRef.current = null;
      }
    };

    worker.postMessage({ nSimulations: simCount });
  }, [simCount]);

  function handleReplay() {
    workerRef.current?.terminate();
    workerRef.current = null;
    setState("idle");
    setMC({ completed: 0, total: 0, winCounts: {}, finalCounts: {}, semiCounts: {}, qfCounts: {}, bestBracket: null });
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
              min={500}
              max={20000}
              step={500}
              value={simCount}
              onChange={(e) => setSimCount(Number(e.target.value))}
              className="sim-slider"
            />
            <div className="sim-range">
              <span>500</span>
              <span>20,000</span>
            </div>
          </div>

          <button className="start-btn" onClick={handleStart}>
            SIMULATE
          </button>
          <p className="start-hint">48 teams · 12 groups · Watch probabilities converge live</p>
        </div>
      </div>
    );
  }

  if (state === "simulating" || state === "converged") {
    return (
      <LiveStats
        completed={mc.completed}
        total={mc.total}
        winCounts={mc.winCounts}
        finalCounts={mc.finalCounts}
        semiCounts={mc.semiCounts}
        liveOdds={liveOdds}
        done={state === "converged"}
        onViewBracket={() => setState("playing")}
      />
    );
  }

  if (mc.bestBracket && state === "playing") {
    return <Bracket result={mc.bestBracket} onComplete={handleReplay} />;
  }

  return null;
}

export default App;
