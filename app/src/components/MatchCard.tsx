import type { MatchResult } from "../data/teams";
import { getFlagUrl } from "../data/teams";

interface Props {
  match: MatchResult;
  animate?: boolean;
}

export function MatchCard({ match, animate = true }: Props) {
  const conf =
    match.probability >= 0.75 ? "high" : match.probability >= 0.6 ? "good" : match.probability >= 0.5 ? "mid" : "low";

  return (
    <div className={`match conf-${conf} ${animate ? "match-reveal" : ""}`}>
      <div className={`team ${match.winner.name === match.teamA.name ? "winner" : "loser"}`}>
        <img className="flag" src={getFlagUrl(match.teamA.iso)} alt="" />
        <span className="name">{match.teamA.name}</span>
      </div>
      <div className={`team ${match.winner.name === match.teamB.name ? "winner" : "loser"}`}>
        <img className="flag" src={getFlagUrl(match.teamB.iso)} alt="" />
        <span className="name">{match.teamB.name}</span>
      </div>
      <span className="prob">{Math.round(match.probability * 100)}%</span>
    </div>
  );
}
