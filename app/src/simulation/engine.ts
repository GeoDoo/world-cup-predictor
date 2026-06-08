import type { Team, MatchResult, GroupStanding } from "../data/teams";
import {
  TEAMS, GROUPS,
  R32_BRACKET, R16_MATCHES, QF_MATCHES, SF_MATCHES, FINAL_MATCH,
} from "../data/teams";

function winProbability(a: Team, b: Team): number {
  return 1.0 / (1.0 + Math.pow(10, (b.points - a.points) / 600));
}

function simulateGroupMatch(a: Team, b: Team): [number, number] {
  const probA = winProbability(a, b);
  const drawProb = 0.25;
  const roll = Math.random();

  if (roll < probA * (1 - drawProb)) {
    const goalsA = weightedChoice([1, 2, 3, 4], [35, 35, 20, 10]);
    const goalsB = Math.floor(Math.random() * goalsA);
    return [goalsA, goalsB];
  } else if (roll < probA * (1 - drawProb) + drawProb) {
    const goals = weightedChoice([0, 1, 2], [30, 45, 25]);
    return [goals, goals];
  } else {
    const goalsB = weightedChoice([1, 2, 3, 4], [35, 35, 20, 10]);
    const goalsA = Math.floor(Math.random() * goalsB);
    return [goalsA, goalsB];
  }
}

function simulateKnockoutMatch(a: Team, b: Team): MatchResult {
  const prob = winProbability(a, b);
  const winner = Math.random() < prob ? a : b;
  return {
    teamA: a,
    teamB: b,
    winner,
    probability: winner === a ? prob : 1 - prob,
  };
}

function weightedChoice(items: number[], weights: number[]): number {
  const total = weights.reduce((s, w) => s + w, 0);
  let r = Math.random() * total;
  for (let i = 0; i < items.length; i++) {
    r -= weights[i];
    if (r <= 0) return items[i];
  }
  return items[items.length - 1];
}

export interface TournamentResult {
  groupStandings: Record<string, GroupStanding[]>;
  knockoutRounds: MatchResult[][];
  champion: Team;
}

export interface MonteCarloResult {
  bestBracket: TournamentResult;
  winProbabilities: Record<string, number>;
  finalProbabilities: Record<string, number>;
  semiProbabilities: Record<string, number>;
  qfProbabilities: Record<string, number>;
  nSimulations: number;
}

export function simulateTournament(): TournamentResult {
  // Group stage
  const groupStandings: Record<string, GroupStanding[]> = {};

  for (const [groupName, teamNames] of Object.entries(GROUPS)) {
    const teams = teamNames.map(n => TEAMS[n]);
    const standings: Record<string, GroupStanding> = {};

    for (const t of teams) {
      standings[t.name] = {
        team: t, played: 0, won: 0, drawn: 0, lost: 0,
        goalsFor: 0, goalsAgainst: 0, points: 0, goalDifference: 0,
      };
    }

    for (let i = 0; i < teams.length; i++) {
      for (let j = i + 1; j < teams.length; j++) {
        const [sa, sb] = simulateGroupMatch(teams[i], teams[j]);
        standings[teams[i].name].played++;
        standings[teams[j].name].played++;
        standings[teams[i].name].goalsFor += sa;
        standings[teams[i].name].goalsAgainst += sb;
        standings[teams[j].name].goalsFor += sb;
        standings[teams[j].name].goalsAgainst += sa;

        if (sa > sb) {
          standings[teams[i].name].won++;
          standings[teams[j].name].lost++;
        } else if (sa === sb) {
          standings[teams[i].name].drawn++;
          standings[teams[j].name].drawn++;
        } else {
          standings[teams[j].name].won++;
          standings[teams[i].name].lost++;
        }
      }
    }

    const sorted = Object.values(standings)
      .map(s => ({
        ...s,
        points: s.won * 3 + s.drawn,
        goalDifference: s.goalsFor - s.goalsAgainst,
      }))
      .sort((a, b) => b.points - a.points || b.goalDifference - a.goalDifference || b.goalsFor - a.goalsFor);

    groupStandings[groupName] = sorted;
  }

  // Determine advancing teams
  const winners: Record<string, Team> = {};
  const runners: Record<string, Team> = {};
  const thirdPlace: { group: string; standing: GroupStanding }[] = [];

  for (const [g, standings] of Object.entries(groupStandings)) {
    winners[g] = standings[0].team;
    runners[g] = standings[1].team;
    thirdPlace.push({ group: g, standing: standings[2] });
  }

  thirdPlace.sort((a, b) =>
    b.standing.points - a.standing.points ||
    b.standing.goalDifference - a.standing.goalDifference ||
    b.standing.goalsFor - a.standing.goalsFor
  );

  const qualifiedThird = thirdPlace.slice(0, 8);
  const thirdByGroup: Record<string, Team> = {};
  for (const { group, standing } of qualifiedThird) {
    thirdByGroup[group] = standing.team;
  }
  const qualifiedGroups = new Set(qualifiedThird.map(t => t.group));

  // Resolve bracket slot to team
  function resolveSlot(slot: string, matchId: string): Team {
    if (slot.startsWith("1")) return winners[slot[1]];
    if (slot.startsWith("2")) return runners[slot[1]];
    // 3rd place: find first available from possible groups
    const possibleGroups = slot.slice(1);
    for (const g of possibleGroups) {
      if (qualifiedGroups.has(g) && thirdByGroup[g]) {
        const team = thirdByGroup[g];
        delete thirdByGroup[g];
        qualifiedGroups.delete(g);
        return team;
      }
    }
    return qualifiedThird[0].standing.team;
  }

  // R32
  const allR32 = [...R32_BRACKET.left, ...R32_BRACKET.right];
  const r32Results: MatchResult[] = [];
  const matchWinners: Record<string, Team> = {};

  for (const { id, slotA, slotB } of allR32) {
    const teamA = resolveSlot(slotA, id);
    const teamB = resolveSlot(slotB, id);
    const result = simulateKnockoutMatch(teamA, teamB);
    r32Results.push(result);
    matchWinners[id] = result.winner;
  }

  // R16
  const r16Results: MatchResult[] = [];
  for (const { id, srcA, srcB } of R16_MATCHES) {
    const result = simulateKnockoutMatch(matchWinners[srcA], matchWinners[srcB]);
    r16Results.push(result);
    matchWinners[id] = result.winner;
  }

  // QF
  const qfResults: MatchResult[] = [];
  for (const { id, srcA, srcB } of QF_MATCHES) {
    const result = simulateKnockoutMatch(matchWinners[srcA], matchWinners[srcB]);
    qfResults.push(result);
    matchWinners[id] = result.winner;
  }

  // SF
  const sfResults: MatchResult[] = [];
  for (const { id, srcA, srcB } of SF_MATCHES) {
    const result = simulateKnockoutMatch(matchWinners[srcA], matchWinners[srcB]);
    sfResults.push(result);
    matchWinners[id] = result.winner;
  }

  // Final
  const finalResult = simulateKnockoutMatch(
    matchWinners[FINAL_MATCH.srcA],
    matchWinners[FINAL_MATCH.srcB]
  );

  return {
    groupStandings,
    knockoutRounds: [r32Results, r16Results, qfResults, sfResults, [finalResult]],
    champion: finalResult.winner,
  };
}

export function monteCarlo(nSimulations: number = 10000): MonteCarloResult {
  const winCounts: Record<string, number> = {};
  const finalCounts: Record<string, number> = {};
  const semiCounts: Record<string, number> = {};
  const qfCounts: Record<string, number> = {};

  let bestBracket: TournamentResult | null = null;
  let bestScore = -1;

  for (let i = 0; i < nSimulations; i++) {
    const result = simulateTournament();
    let score = 0;

    for (const match of result.knockoutRounds[0]) score += match.probability;
    for (const match of result.knockoutRounds[1]) score += match.probability;

    for (const match of result.knockoutRounds[2]) {
      qfCounts[match.winner.name] = (qfCounts[match.winner.name] || 0) + 1;
      score += match.probability;
    }

    for (const match of result.knockoutRounds[3]) {
      semiCounts[match.winner.name] = (semiCounts[match.winner.name] || 0) + 1;
      score += match.probability;
    }

    const finalMatch = result.knockoutRounds[4][0];
    finalCounts[finalMatch.teamA.name] = (finalCounts[finalMatch.teamA.name] || 0) + 1;
    finalCounts[finalMatch.teamB.name] = (finalCounts[finalMatch.teamB.name] || 0) + 1;
    winCounts[result.champion.name] = (winCounts[result.champion.name] || 0) + 1;
    score += finalMatch.probability;

    if (score > bestScore) {
      bestScore = score;
      bestBracket = result;
    }
  }

  const toPct = (counts: Record<string, number>) => {
    const out: Record<string, number> = {};
    for (const [k, v] of Object.entries(counts)) out[k] = v / nSimulations;
    return out;
  };

  return {
    bestBracket: bestBracket!,
    winProbabilities: toPct(winCounts),
    finalProbabilities: toPct(finalCounts),
    semiProbabilities: toPct(semiCounts),
    qfProbabilities: toPct(qfCounts),
    nSimulations,
  };
}
