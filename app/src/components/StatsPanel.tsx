import { useState } from "react";
import type { MonteCarloResult } from "../simulation/engine";
import { getFlagUrl, TEAMS } from "../data/teams";

interface Props {
  result: MonteCarloResult;
}

export function StatsPanel({ result }: Props) {
  const [open, setOpen] = useState(true);

  const sorted = Object.entries(result.winProbabilities)
    .sort(([, a], [, b]) => b - a);

  if (!open) {
    return (
      <button className="stats-toggle" onClick={() => setOpen(true)}>
        📊 Show Win Probabilities
      </button>
    );
  }

  return (
    <div className="stats-panel">
      <div className="stats-header">
        <div>
          <span className="stats-title">WIN PROBABILITIES</span>
          <span className="stats-sub">{result.nSimulations.toLocaleString()} simulations</span>
        </div>
        <button className="stats-close" onClick={() => setOpen(false)}>×</button>
      </div>
      <div className="stats-list">
        {sorted.map(([name, winPct], i) => {
          const team = TEAMS[name];
          if (!team) return null;
          const finalPct = result.finalProbabilities[name] || 0;
          const semiPct = result.semiProbabilities[name] || 0;

          return (
            <div key={name} className="stats-row">
              <span className="stats-rank">{i + 1}</span>
              <img className="stats-flag" src={getFlagUrl(team.iso)} alt="" />
              <span className="stats-name">{name}</span>
              <div className="stats-bar-wrap">
                <div
                  className="stats-bar"
                  style={{ width: `${Math.max(winPct * 100 / (sorted[0][1] || 1) * 100, 2)}%` }}
                />
              </div>
              <span className="stats-pct">{(winPct * 100).toFixed(1)}%</span>
              <div className="stats-extra">
                <span title="Final appearance">F {(finalPct * 100).toFixed(0)}%</span>
                <span title="Semi-final appearance">SF {(semiPct * 100).toFixed(0)}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
