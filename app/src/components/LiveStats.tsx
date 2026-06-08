import type { LiveOdds } from "../data/odds-api";
import { getFlagUrl, TEAMS } from "../data/teams";

interface Props {
  completed: number;
  total: number;
  winCounts: Record<string, number>;
  finalCounts: Record<string, number>;
  semiCounts: Record<string, number>;
  liveOdds: Record<string, LiveOdds>;
  done: boolean;
  onViewBracket: () => void;
}

export function LiveStats({
  completed, total, winCounts, finalCounts, semiCounts, liveOdds, done, onViewBracket,
}: Props) {
  const sorted = Object.entries(winCounts)
    .map(([name, count]) => ({
      name,
      winPct: completed > 0 ? count / completed : 0,
      finalPct: completed > 0 ? (finalCounts[name] || 0) / completed : 0,
      semiPct: completed > 0 ? (semiCounts[name] || 0) / completed : 0,
      odds: liveOdds[name],
    }))
    .sort((a, b) => b.winPct - a.winPct);

  const maxPct = sorted[0]?.winPct || 0;
  const pctDone = total > 0 ? (completed / total) * 100 : 0;

  const leader = sorted[0];
  const leaderTeam = leader ? TEAMS[leader.name] : null;

  return (
    <div className="cinema live-screen">
      <div className="live-header">
        <div className="live-counter-wrap">
          <span className="live-label">MONTE CARLO SIMULATION</span>
          <div className="live-counter">
            <span className="live-num">{completed.toLocaleString()}</span>
            <span className="live-slash"> / </span>
            <span className="live-total">{total.toLocaleString()}</span>
          </div>
          <div className="live-progress">
            <div className="live-progress-fill" style={{ width: `${pctDone}%` }} />
          </div>
        </div>

        {leaderTeam && (
          <div className="live-leader">
            <img className="live-leader-flag" src={getFlagUrl(leaderTeam.iso)} alt="" />
            <div>
              <div className="live-leader-name">{leader.name}</div>
              <div className="live-leader-pct">{(leader.winPct * 100).toFixed(1)}% to win</div>
            </div>
          </div>
        )}
      </div>

      <div className="live-col-headers">
        <span></span><span></span><span></span>
        <span></span>
        <span>SIM</span>
        <span className="col-right" style={{gridColumn: "span 2"}}>BETTING ODDS (LIVE)</span>
      </div>
      <div className="live-list">
        {sorted.map((entry, i) => {
          const team = TEAMS[entry.name];
          if (!team) return null;
          const barWidth = maxPct > 0 ? (entry.winPct / maxPct) * 100 : 0;

          return (
            <div key={entry.name} className="live-row" style={{ order: i }}>
              <span className="live-rank">{i + 1}</span>
              <img className="live-flag" src={getFlagUrl(team.iso)} alt="" />
              <span className="live-name">{entry.name}</span>
              <div className="live-bar-wrap">
                <div className="live-bar" style={{ width: `${Math.max(barWidth, 1)}%` }} />
              </div>
              <span className="live-pct">{(entry.winPct * 100).toFixed(1)}%</span>
              {entry.odds ? (
                <>
                  <span className="live-odds">+{entry.odds.american}</span>
                  <span className="live-odds-pct">{(entry.odds.implied * 100).toFixed(1)}%</span>
                </>
              ) : (
                <>
                  <span className="live-odds dim">—</span>
                  <span className="live-odds-pct dim">—</span>
                </>
              )}
            </div>
          );
        })}
      </div>

      {done && (
        <div className="live-done-bar">
          <span className="live-done-text">SIMULATION COMPLETE</span>
          <button className="live-bracket-btn" onClick={onViewBracket}>
            VIEW BEST BRACKET →
          </button>
        </div>
      )}
    </div>
  );
}
