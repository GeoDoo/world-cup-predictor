import { useState, useEffect, useRef } from "react";
import type { MatchResult, GroupStanding } from "../data/teams";
import { getFlagUrl } from "../data/teams";
import type { TournamentResult } from "../simulation/engine";
import { MatchCard } from "./MatchCard";

interface Props {
  result: TournamentResult;
  onComplete: () => void;
}

type Phase = "groups" | "r32" | "r16" | "qf" | "sf" | "final" | "winner";

const ROUND_LABELS = ["ROUND OF 32", "ROUND OF 16", "QUARTER-FINALS", "SEMI-FINALS", "FINAL"];
const ROUND_DELAY = [500, 800, 1100, 1500, 2500];

export function Bracket({ result, onComplete }: Props) {
  const [phase, setPhase] = useState<Phase>("groups");
  const [visibleGroups, setVisibleGroups] = useState<number>(0);
  const [visibleMatches, setVisibleMatches] = useState<number[]>([0, 0, 0, 0, 0]);
  const [showWinner, setShowWinner] = useState(false);
  const cancelled = useRef(false);

  useEffect(() => {
    cancelled.current = false;
    runAnimation();
    return () => { cancelled.current = true; };
  }, [result]);

  async function runAnimation() {
    // Groups phase
    setPhase("groups");
    for (let i = 0; i <= 12; i++) {
      if (cancelled.current) return;
      setVisibleGroups(i);
      await sleep(300);
    }
    await sleep(2000);

    // Knockout phases
    const phases: Phase[] = ["r32", "r16", "qf", "sf", "final"];
    for (let r = 0; r < 5; r++) {
      if (cancelled.current) return;
      setPhase(phases[r]);
      const matchCount = result.knockoutRounds[r].length;
      for (let m = 0; m <= matchCount; m++) {
        if (cancelled.current) return;
        setVisibleMatches(prev => {
          const next = [...prev];
          next[r] = m;
          return next;
        });
        if (m < matchCount) await sleep(ROUND_DELAY[r]);
      }
      await sleep(800);
    }

    // Winner
    await sleep(1500);
    if (cancelled.current) return;
    setPhase("winner");
    setShowWinner(true);
    onComplete();
  }

  const phaseLabel = phase === "groups" ? "GROUP STAGE" :
    phase === "winner" ? "" :
    ROUND_LABELS[["r32", "r16", "qf", "sf", "final"].indexOf(phase)];

  if (phase === "groups") {
    return (
      <div className="cinema">
        <div className="phase-label">{phaseLabel}</div>
        <div className="groups-grid">
          {Object.entries(result.groupStandings).slice(0, visibleGroups).map(([name, standings]) => (
            <GroupCard key={name} name={name} standings={standings} />
          ))}
        </div>
      </div>
    );
  }

  if (showWinner) {
    return (
      <div className="cinema winner-overlay">
        <div className="winner-content">
          <div className="winner-trophy">🏆</div>
          <img className="winner-flag" src={getFlagUrl(result.champion.iso)} alt="" />
          <div className="winner-name">{result.champion.name}</div>
          <div className="winner-sub">WORLD CUP CHAMPION 2026</div>
        </div>
        <a className="home-link" href="#" onClick={(e) => { e.preventDefault(); onComplete(); }}>
          ↻ New Simulation
        </a>
      </div>
    );
  }

  // Knockout bracket
  const r32 = result.knockoutRounds[0];
  const r16 = result.knockoutRounds[1];
  const qf = result.knockoutRounds[2];
  const sf = result.knockoutRounds[3];
  const final = result.knockoutRounds[4];

  const leftRounds = [r32.slice(0, 8), r16.slice(0, 4), qf.slice(0, 2), [sf[0]]];
  const rightRounds = [r32.slice(8), r16.slice(4), qf.slice(2), [sf[1]]];

  function getVisibleCount(roundIdx: number, side: "left" | "right"): number {
    const total = visibleMatches[roundIdx];
    const halfSize = result.knockoutRounds[roundIdx].length / 2;
    if (side === "left") return Math.min(total, halfSize);
    return Math.max(0, total - halfSize);
  }

  return (
    <div className="cinema">
      <div className="phase-label">{phaseLabel}</div>
      <div className="bracket">
        <div className="bracket-half left">
          {leftRounds.map((matches, rIdx) => (
            <div key={rIdx} className={`round r${rIdx}`}>
              {matches.slice(0, getVisibleCount(rIdx, "left")).map((m, i) => (
                <MatchCard key={i} match={m} />
              ))}
            </div>
          ))}
        </div>

        <div className="bracket-center">
          {visibleMatches[4] > 0 && (
            <div className="final-box match-reveal">
              <div className="final-trophy">🏆</div>
              <div className="final-label">FINAL</div>
              <div className="final-matchup">
                <div className={`team ${final[0].winner.name === final[0].teamA.name ? "winner" : "loser"}`}>
                  <img className="flag" src={getFlagUrl(final[0].teamA.iso)} alt="" />
                  <span className="name">{final[0].teamA.name}</span>
                </div>
                <div className="vs">vs</div>
                <div className={`team ${final[0].winner.name === final[0].teamB.name ? "winner" : "loser"}`}>
                  <img className="flag" src={getFlagUrl(final[0].teamB.iso)} alt="" />
                  <span className="name">{final[0].teamB.name}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bracket-half right">
          {rightRounds.map((matches, rIdx) => (
            <div key={rIdx} className={`round r${rIdx}`}>
              {matches.slice(0, getVisibleCount(rIdx, "right")).map((m, i) => (
                <MatchCard key={i} match={m} />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GroupCard({ name, standings }: { name: string; standings: GroupStanding[] }) {
  return (
    <div className="group-card">
      <div className="group-name">Group {name}</div>
      <table>
        <thead>
          <tr><th></th><th>Team</th><th>P</th><th>GD</th><th>Pts</th></tr>
        </thead>
        <tbody>
          {standings.map((s, i) => (
            <tr key={s.team.name} className={i < 2 ? "qualified" : i === 2 ? "third" : "out"}>
              <td><img className="flag-sm" src={getFlagUrl(s.team.iso)} alt="" /></td>
              <td className="team-cell">{s.team.name}</td>
              <td>{s.played}</td>
              <td>{s.goalDifference > 0 ? `+${s.goalDifference}` : s.goalDifference}</td>
              <td className="pts">{s.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function sleep(ms: number) {
  return new Promise(r => setTimeout(r, ms));
}
